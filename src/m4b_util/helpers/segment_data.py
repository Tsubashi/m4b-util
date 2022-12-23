"""Segment Data."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SegmentData:
    """Represents a single segment from an audio file, such as a chapter or a non-silence area.

    Variables dealing with times should be in seconds.
    """
    start_time: float
    end_time: float
    id: int = None
    title: str = None
    backing_file: Path = None
    file_start_time: float = None
    file_end_time: float = None

    def __setattr__(self, key, value):
        """Make sure all the 'time' variables are rounded to three decimal places (miliseconds)."""
        if "time" in key and value is not None:
            value = round(value, 3)
        super().__setattr__(key, value)
