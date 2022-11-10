"""Helper functions for running FFMPEG."""
import re
import subprocess

from rich.progress import Progress, SpinnerColumn


def to_ms(hour=0, min=0, sec=0, ms=0):
    """Convert from hrs:min:sec.ms to straight milliseconds."""
    result = (int(hour) * 60 * 60 * 1000) + (int(min) * 60 * 1000) + (int(sec) * 1000) + int(ms)
    return result


class FFProgress:
    """Represents a single run of an ffmpeg command."""
    DUR_REGEX = re.compile(r"Duration: (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})")
    TIME_REGEX = re.compile(r"out_time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})")

    def __init__(self, cmd) -> None:
        """Initialize the FfmpegProgress class.

        :param cmd: A list of command line elements, e.g. ["ffmpeg", "-i", ...]
        """
        self.cmd = cmd
        self.output = None

    def run(self):
        """Run an ffmpeg command, trying to capture the process output and calculate the duration / progress.

        Yields the progress in percent.
        """
        total_dur = None

        # Make sure the command has -progress and -nostats
        cmd_with_progress = ([self.cmd[0]] + ["-progress", "-", "-nostats"] + self.cmd[1:])

        stdout = []

        p = subprocess.Popen(
            cmd_with_progress,
            stdin=subprocess.PIPE,  # Apply stdin isolation by creating separate pipe.
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
        )

        yield 0

        while True:
            # If there isn't anything new to process, just keep spinning.
            line = p.stdout
            if line is None:
                continue

            # Clean up the line we got from subprocess
            stdout_line = line.readline().decode("utf-8", errors="replace").strip()

            # Check if it is time to exit
            if stdout_line == "" and p.poll() is not None:
                break

            # Add what we got to our internal track of stderr
            stdout.append(stdout_line.strip())
            self.output = "\n".join(stdout)

            # Check out regexes
            if total_dur is None:  # We haven't found the initial duration yet
                total_dur_match = FFProgress.DUR_REGEX.search(stdout_line)
                if total_dur_match:
                    total_dur = total_dur_match.groupdict()
                    total_dur = to_ms(**total_dur)
            else:  # We already know our duration, lets see if we have an update
                progress_time = FFProgress.TIME_REGEX.search(stdout_line)
                if progress_time:
                    elapsed_time = to_ms(**progress_time.groupdict())
                    yield (elapsed_time / total_dur) * 100

        # Throw an exception if ffmpeg didn't exit cleanly
        if p.returncode != 0:
            self.output = "\n".join(stdout)
            raise RuntimeError(f"Error running command {str(self.cmd)}: {self.output}")

        # We've got nothing else to give, so mark it as 100% done
        yield 100


def run(cmd, task_name, progress=None):
    """Run ffmpeg command and show progress.

    :param cmd: Command to run
    :param task_name: Text to print in front of progress bar
    :param progress: An existing progress object. If not given, one will be created.

    :return FFProgress instance
    """
    progress_needs_stopping = False
    if progress is None:
        progress = Progress(SpinnerColumn(), *Progress.get_default_columns())
        progress.start()
        progress_needs_stopping = True
    ff = FFProgress(cmd)
    current_percent = 0

    try:
        task = progress.add_task(f"[cyan]{task_name}", total=100)
        for percent in ff.run():
            advance_amount = percent - current_percent
            progress.update(task, advance=advance_amount)
            current_percent = percent
    except RuntimeError as e:
        progress.console.print("[bold red]Error:[/] Something went wrong with ffmpeg:")
        progress.console.print(e)
        progress.stop()
        return None
    progress.update(task, completed=100)

    if progress_needs_stopping:
        progress.stop()

    return ff
