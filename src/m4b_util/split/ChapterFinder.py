"""Chapter Finder."""
from dataclasses import dataclass
from pathlib import Path

from m4b_util.helpers import ffprobe
from .SegmentData import SegmentData


@dataclass
class ChapterFinder:
    """Reads chapter metadata from a file and generates a list of matching SegmentData's."""
    input_path: Path
    start_time: float = 0.0
    end_time: float = 0.0

    def find(self):
        """Read chapter metadata into an object."""
        start_time = self.start_time or 0
        end_time = self.end_time or 100000000000000.0
        probe = ffprobe.run_probe(self.input_path)
        if probe is None:
            return []  # If we can't read the file, then we didn't find any chapters.
        chapter_list = list()
        for chapter in probe.chapters:
            title = chapter.get("tags", dict()).get("title")
            if float(chapter['start_time']) >= start_time and float(chapter['end_time']) <= end_time:
                chapter_list.append(SegmentData(
                    id=chapter['id'],
                    start_time=float(chapter['start_time']),
                    end_time=float(chapter['end_time']),
                    title=title
                ))
        return chapter_list
