"""Binder Class."""
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import mkdtemp

from rich import print
from rich.status import Status

from ..helpers import ffprobe, ffprogress
from ..helpers.ParallelFFmpeg import ParallelFFmpeg


class Binder:
    """Read and store all the info we need to bind the audiobook."""

    def __init__(self):
        """Set default values."""
        # Config Related
        self.use_filename = False
        self.decode_durations = False
        self.keep_temp_files = False

        # File Related
        self.files = list()
        self.temp_files = list()
        self.temp_path = Path(mkdtemp(prefix="m4b-util"))
        self.final_file = self.temp_path / "finished.m4b"
        self.output_name = None
        self.output_dir = None

        # Metadata related
        self.chapters = list()
        self.title = None
        self.author = None
        self.date = None
        self.cover = None
        # Set duration to a big number, (hopefully larger than our actual duration)
        # just in case we try to write chapters without knowing the final duration.
        self.duration = 100000000000

    @property
    def output_path(self):
        """Calculate output path based on what we currently know."""
        # Use a default is self.output_name is not set.
        name = self.output_name or f"{self.author} - {self.title}.m4b"

        # Make sure it ends with .m4b
        if not name.endswith(".m4b"):
            name = f"{name}.m4b"

        # Use current dir if self.output_dir is not set.
        if self.output_dir:
            final_path = Path(self.output_dir)
        else:
            final_path = Path()
        return final_path / name

    @property
    def metadata(self):
        """Generate the metadata text when requested, since it depends on the current state of the object."""
        # Start by writing the global header
        metadata = (";FFMETADATA1\n"
                    "major_brand=M4A\n"
                    "minor_version=512\n"
                    "compatible_brands=M4A isomiso2\n"
                    f"title={self.title}\n"
                    f"artist={self.author}\n"
                    f"album={self.title}\n"
                    f"date={self.date}\n"
                    "genre=Audiobook\n"
                    )
        # Add one last entry to our chapter list, to mark the end of the file. This will not get written to the file.
        tmp_chapters = self.chapters.copy()
        tmp_chapters.append({"title": "The Very End of the Book", "startTime": self.duration})

        # Then add chapters to metadata
        for i in range(len(tmp_chapters) - 1):
            title = tmp_chapters[i]['title']
            start = tmp_chapters[i]['startTime']
            end = tmp_chapters[i + 1]['startTime'] - 1
            metadata += ("[CHAPTER]\n"
                         "TIMEBASE=1/1000\n"
                         f"START={start}\n"
                         f"END={end}\n"
                         f"title={title}\n"
                         )
        return metadata

    def bind(self):
        """Bind together an audiobook, based on what we know."""
        if self.keep_temp_files:
            print(f"[yellow]Info:[/] Temp files can be found at [yellow]{self.temp_path}[/]")

        # Make sure we actually have files to convert
        if len(self.files) == 0:
            print("[bold red]Error:[/] No input files found.")
            return False

        # First, convert all audios to m4a, in parallel.
        p = ParallelFFmpeg("Converting files to m4a")
        tasks = list()
        for file in self.files:
            # Determine what to call the output file
            out_m4a = self.temp_path / f"{file.stem}.m4a"

            # Record the file for concatenation later
            self.temp_files.append(out_m4a)

            # Write the FFMPEG command
            cmd = ["ffmpeg", "-i", file, "-filter_complex", "[0:a]asetpts=N/SR/TB[s0]", "-map", "[s0]",
                   "-c:a", "aac", out_m4a, "-y"]
            tasks.append({
                "name": file.stem,
                "command": cmd
            })
        p.process(tasks)

        # Scan the files we just converted for info
        self._scan_files(self.temp_files)

        # Next, concatenate those m4a files into an m4b
        long_file = self._concatenate_all_audio_files()

        # Now, add chapter self
        coverless_file = self._add_chapter_info(long_file)

        # Add cover artwork if specified, otherwise just copy the previous output
        if self.cover:
            covered_file = self._add_cover(coverless_file)
            shutil.move(covered_file, self.final_file)
        else:
            shutil.move(coverless_file, self.final_file)

        # Copy the output into place
        print("[cyan]Copying output.")
        shutil.copy(self.final_file, self.output_path)

        # Clean up
        if not self.keep_temp_files:
            shutil.rmtree(self.temp_path)

        return True

    def _scan_files(self, files):
        """Scan a list of files and update based on them.

        :param files: List of files to scan.
        """
        # Set up variables
        time_counter = 0
        segment_counter = 0

        # Start our status tracker
        print("[cyan]Collecting file data...[/]")
        file_scan_status = Status("Starting")
        file_scan_status.start()

        # Scan all the files
        for file in files:
            file_scan_status.update(f"Scanning {file.name}")
            # Count which segment we are on. Used in case the chapter has no title.
            segment_counter += 1

            # Run ffprobe and parse the output.
            probe = ffprobe.run_probe(file)
            if not probe or probe.audio is None:
                print(f"[bold yellow]Warning:[/] Unable to parse '[bold white]{file}[/]'. Skipping.")
                continue

            # Attempt to fill any missing metadata
            chapter_title = None
            if probe.tags:  # pragma: no branch - None of our test files hit this, but some other audio formats might.
                self.title = self.title or probe.tags.get('album')
                self.author = self.author or probe.tags.get('artist')
                self.date = self.date or probe.tags.get('date')
                chapter_title = probe.tags.get('title')

            if self.use_filename:
                chapter_title = file.stem
            if not chapter_title:
                chapter_title = segment_counter
            self.chapters.append({"title": chapter_title, "startTime": time_counter})

            # Add our duration to the counter for use as the next chapter's start point
            try:
                time_counter += self._get_duration(file)
            except RuntimeError:
                print(f"[yellow]Warning:[/] Failed to determine duration of '[bold white]{file}[/]'. Ignoring.")
                self.chapters.pop()

        # Mark the total duration of all files.
        self.duration = time_counter

        # Shut off the status tracker and alert the user
        file_scan_status.stop()
        print("[green]File scan complete.")

    def _get_duration(self, file):
        """Determine the duration of a file.

        If self.decode_durations is set, run the file through ffmpeg to get the time.
        Otherwise, get it from the metadata.

        :param file: The audio file to run through ffmpeg

        :return The duration of the file, in milliseconds
        """
        duration = None
        if self.decode_durations:
            # Setup variables
            time_regex = re.compile(r"time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})")
            time_match = None

            # Run the decoder
            cmd = ["ffmpeg", "-i", file, "-loglevel", "info", "-nostats", "-f", "null", "-"]
            p = subprocess.run(cmd, capture_output=True)

            # Search for time messages
            for line in p.stderr.decode('utf-8', errors="replace").splitlines():
                match = time_regex.search(line)
                if match:
                    time_match = match  # Only keep the most recent

            # Set the duration if we found any
            if time_match:
                duration = time_match.groupdict()
                duration = ffprogress.to_ms(**duration)
            else:
                print(f"[bold yellow]Warning:[/] Unable to find duration of '[bold white]{file.name}[/]' "
                      "during decoding. Falling back to metadata.")

        if not duration:  # Use the metadata as given
            probe = ffprobe.run_probe(file)
            if not probe or probe.audio is None:
                raise RuntimeError("Could not get audio stream.")
            try:
                seconds = float(probe.audio.get('duration'))
            except TypeError:
                raise RuntimeError("Cannot parse duration listed in file.")
            duration = int(seconds * 1000)  # Convert to milliseconds

        return duration

    def _concatenate_all_audio_files(self):
        """Bring all the input files, now m4a, and put them into an m4b."""
        # Start by writing the filelist to a temp file.
        filelist_file = self.temp_path / "filelist"
        with open(filelist_file, 'w') as f:
            for file in self.temp_files:
                # Single quotes in filenames need to be replaced with `'\''` to work with ffmpeg
                # https://superuser.com/questions/787064/filename-quoting-in-ffmpeg-concat
                safer_filename = str(file).replace("'", "'\\''")
                f.write(f"file '{safer_filename}'\n")

        # Then use that file to concatenate everything.
        output_file = self.temp_path / "long.m4a"
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", filelist_file, "-c", "copy", output_file]
        self._run_ffmpeg(cmd, "Combining Audio Files.")

        # Cleanup, if applicable
        if not self.keep_temp_files:
            for file in self.temp_files:
                file.unlink()

        return output_file

    def _add_chapter_info(self, input_file):
        """Add chapter info to an m4b file."""
        # Write the metadata to a temp file.
        metadata_file = self.temp_path / "ffmetadata"
        with open(metadata_file, 'w') as f:
            print(self.metadata, file=f)

        output_file = self.temp_path / "coverless.m4b"
        cmd = ["ffmpeg", "-y", "-i", input_file, "-i", metadata_file, "-map_metadata", "1", "-map_chapters", "1",
               "-c", "copy", output_file]
        self._run_ffmpeg(cmd, "Converting to .m4b")

        # Cleanup, if applicable
        if not self.keep_temp_files:
            input_file.unlink()

        return output_file

    def _add_cover(self, input_file):
        """Add a cover to an m4b."""
        output_file = self.temp_path / "covered.m4b"
        cmd = ["ffmpeg", "-y", "-i", input_file, "-i", self.cover, "-map", "0:a", "-map", "1",
               "-c", "copy", "-disposition:v:0", "attached_pic", output_file]
        self._run_ffmpeg(cmd, "Adding Cover")

        # Cleanup, if applicable
        if not self.keep_temp_files:
            input_file.unlink()

        return output_file

    def _run_ffmpeg(self, cmd, message):
        if not ffprogress.run(cmd, message):
            print("[bold red]Error:[/] ffmpeg failed.")
            if not self.keep_temp_files:
                shutil.rmtree(self.temp_path)
            exit(1)
