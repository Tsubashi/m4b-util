"""Chapter Finder."""
from m4b_util.helpers import ffprobe
from .SegmentData import SegmentData


class ChapterFinder:
    """Reads chapter metadata from a file and generates a list of matching SegmentData's."""

    def __init__(self):
        """Set Defaults."""
        self.input_path = None

    def find(self):
        """Read chapter metadata into an object."""
        probe = ffprobe.run_probe(self.input_path)
        chapter_list = list()
        for chapter in probe.chapters:
            title = chapter.get("tags", dict()).get("title")
            chapter_list.append(SegmentData(
                id=chapter['id'],
                start_time=float(chapter['start_time']),
                end_time=float(chapter['end_time']),
                title=title
            ))
        return chapter_list
