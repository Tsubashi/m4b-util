"""Silence Finder."""
from dataclasses import dataclass, field
from pathlib import Path
import re

from m4b_util.helpers import ffprogress
from .SegmentData import SegmentData


@dataclass
class SilenceFinder:
    """Finds silence in a file and generates a list of SegmentData's representing the non-silence portions."""
    input_path: Path
    start_time: float = 0.0
    end_time: float = 0.0
    silence_duration: float = 3.0
    silence_threshold: int = -35
    _ffoutput: list = field(init=False, repr=False)

    def find(self):
        self._run_silencedetect()
        times = self._get_segment_times()
        if not times:
            return list()

        # Generate SegmentData list
        retval = list()
        for i, (start_time, end_time) in enumerate(times):
            retval.append(SegmentData(
                id=i,
                start_time=start_time,
                end_time=end_time,
            ))
        return retval

    def _run_silencedetect(self):
        """Run the silencedetect filter from ffmpeg and return the output lines."""
        # Run ffmpeg's silencedetect filter
        cmd = ["ffmpeg", "-i", self.input_path]
        if self.start_time:
            cmd.extend(["-ss", str(self.start_time)])
        if self.end_time:
            cmd.extend(["-to", str(self.end_time)])
        cmd.extend([
            "-filter_complex",
            f"[0]silencedetect=d={self.silence_duration}:n={self.silence_threshold}dB[s0]",
            "-map", "[s0]",
            "-f", "null",
            "-"
        ])
        ff = ffprogress.run(cmd, "Detecting Silence")

        # Check to see if ffmpeg exited abnormally
        if ff is None:
            print("[bold red]Error:[/] Could not determine segment times.")
            exit(1)
        self._ffoutput = ff.output.splitlines()

    def _get_segment_times(self):
        """Compute non-silence segment start and end times."""
        silence_start_re = re.compile(r' silence_start: (?P<start>[0-9]+(\.?[0-9]*))$')
        silence_end_re = re.compile(r' silence_end: (?P<end>[0-9]+(\.?[0-9]*)) ')
        total_duration_re = re.compile(
            r'size=[^ ]+ time=(?P<hours>[0-9]{2}):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9\.]{5}) bitrate=')
        # Segments start when silence ends, and segments end when silence starts.
        segment_starts = []
        segment_ends = []
        start_time = self.start_time or 0
        end_time = 10000000.0
        for line in self._ffoutput:
            # Check for silence start
            silence_start_match = silence_start_re.search(line)
            if silence_start_match:
                segment_ends.append(float(silence_start_match.group('start')))
                if len(segment_starts) == 0:
                    # Started with non-silence.
                    segment_starts.append(start_time)
                continue

            # Check for silence end
            silence_end_match = silence_end_re.search(line)
            if silence_end_match:
                segment_starts.append(float(silence_end_match.group('end')))
            total_duration_match = total_duration_re.search(line)

            # Check for duration
            if total_duration_match:
                hours = int(total_duration_match.group('hours'))
                minutes = int(total_duration_match.group('minutes'))
                seconds = float(total_duration_match.group('seconds'))
                end_time = hours * 3600 + minutes * 60 + seconds

        if len(segment_starts) == 0:
            # No silence found.
            return None

        if len(segment_starts) > len(segment_ends):
            # Finished with non-silence.
            segment_ends.append(end_time)

        output = list(zip(segment_starts, segment_ends))

        return output

