"""Segment Data."""
from dataclasses import dataclass


@dataclass
class SegmentData:
    """Represents a single segment from an audio file, such as a chapter or a non-silence area."""
    start_time: float
    end_time: float
    id: int = None
    title: str = None
