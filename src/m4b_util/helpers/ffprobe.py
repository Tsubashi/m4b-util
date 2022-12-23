"""Helper functions for running ffprobe."""
import json
import re
from subprocess import run


class Probe:
    """Holds the results from an ffprobe run."""
    def __init__(self, ffprobe_output):
        """Set up attributes."""
        self.data = json.loads(ffprobe_output)
        self.streams = self.data.get('streams', None)
        self.audio = self.first_stream_of(codec_type="audio")
        self.format = self.data.get('format')
        self.tags = self.data.get('format', dict()).get('tags', None)
        self.chapters = self.data.get('chapters')

    def first_stream_of(self, codec_type):
        """Get the first stream matching the requested arguments.

        For now, "type" is the only thing we care about, but maybe in the future we will want to filter on other fields?

        :param codec_type: Stream type. Usually "audio" or "video".
        :return: List representing the first matching stream
        """
        for stream in self.data.get('streams'):
            if stream.get("codec_type") == codec_type:
                return stream

        # No stream matches
        return None


def run_probe(file):
    """Run ffprobe on the specified file and return a JSON representation of the output."""
    cmd = ["ffprobe", "-show_format", "-show_streams", "-show_chapters", "-of", "json", "-i", file]

    p = run(cmd, capture_output=True)
    if p.returncode != 0:
        return None
    return Probe(p.stdout.decode('utf-8'))


def get_file_duration(file, decode_duration=False):
    """Determine the duration of a file.

    If self.decode_durations is set, run the file through ffmpeg to get the time.
    Otherwise, get it from the metadata.

    :param file: The audio file to run through ffmpeg
    :param decode_duration: Actually decode the file to find duration, instead of relying on metadata.

    :return The duration of the file, in seconds
    """
    duration = None
    if decode_duration:
        # Setup variables
        time_regex = re.compile(r"time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})")
        time_match = None

        # Run the decoder
        cmd = ["ffmpeg", "-i", file, "-loglevel", "info", "-nostats", "-f", "null", "-"]
        p = run(cmd, capture_output=True)

        # Search for time messages
        for line in p.stderr.decode('utf-8', errors="replace").splitlines():
            match = time_regex.search(line)
            if match:
                time_match = match  # Only keep the most recent

        # Set the duration if we found any
        if time_match:
            match = time_match.groupdict()
            duration = ((int(match["hour"]) * 60 * 60)
                        + (int(match["min"]) * 60)
                        + int(match["sec"])
                        + (int(match["ms"]) / 100))
        else:
            print(f"[bold yellow]Warning:[/] Unable to find duration of '[bold white]{file.name}[/]' "
                  "during decoding. Falling back to metadata.")

    if not duration:  # Use the metadata as given
        probe = run_probe(file)
        if not probe or probe.audio is None:
            raise RuntimeError("Could not get audio stream.")
        try:
            seconds = float(probe.audio.get('duration'))
        except TypeError:
            raise RuntimeError("Cannot parse duration listed in file.")
        duration = seconds

    return duration
