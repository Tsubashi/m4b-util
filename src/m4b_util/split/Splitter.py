"""The Splitter Class."""
from dataclasses import dataclass
from pathlib import Path

from m4b_util.helpers.ParallelFFmpeg import ParallelFFmpeg
from m4b_util.helpers import cover_utils


@dataclass
class Splitter:
    """Holds all the info and methods for splitting a file."""
    input_path: Path
    output_dir_path: Path
    segment_list: list

    output_pattern: str = "segment_{i:04d}.mp3"

    def split(self):
        """Do the actual splitting."""
        cover_utils.extract_cover(self.input_path, self.output_dir_path / "cover.png")

        # Generate task list
        tasks = list()
        for i, segment in enumerate(self.segment_list):
            time = segment.end_time - segment.start_time

            self.output_dir_path.mkdir(exist_ok=True)
            output_path = self.output_dir_path / self.output_pattern.format(i, i=i, title=segment.title)

            cmd = ["ffmpeg", "-ss", str(segment.start_time), "-t", str(time), "-i", self.input_path,
                   "-map", "0:a", "-map_chapters", "-1", "-y"]
            if segment.title:
                cmd.extend(["-metadata", f"title={segment.title}"])
            cmd.append(output_path)

            name = f"Splitting segment {i}"
            if segment.title:
                name += f" - {segment.title}"
            tasks.append({
                "name": name,
                "command": cmd
            })

        # Process splits in parallel
        p = ParallelFFmpeg(f"Splitting '{self.input_path.name}'")
        p.process(tasks)




