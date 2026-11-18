"""Cue sheet conversion utilities."""

from __future__ import annotations

# Standard Library
import re
from typing import Iterable, List

from .segment_data import SegmentData


def cue_time_to_seconds(cue_time: str) -> float:
    """Convert cue sheet time into seconds."""
    minute, second, frame = [int(x) for x in cue_time.split(":")]
    return minute * 60 + second + frame / 75


def seconds_to_cue_time(seconds: float) -> str:
    """Convert seconds into cue sheet time."""
    total_frames = round(seconds * 75)
    minutes, remainder = divmod(total_frames, 75 * 60)
    secs, frames = divmod(remainder, 75)
    return f"{minutes:02d}:{secs:02d}:{frames:02d}"


def segment_data_from_cue(lines: Iterable[str]) -> List[SegmentData]:
    """Convert cue sheet lines to a list of segments."""
    segments: List[SegmentData] = []
    previous = None
    current_title = None
    cue_regex = re.compile(r"^\s*INDEX\s+01\s+(?P<time>\d{2}:\d{2}:\d{2})")
    title_regex = re.compile(r"^\s*TITLE\s+\"?(?P<title>.+?)\"?$")
    for line in lines:
        title_match = title_regex.search(line)
        if title_match:
            current_title = title_match["title"]
            continue
        match = cue_regex.search(line)
        if match:
            if previous:
                segments.append(
                    SegmentData(
                        start_time=previous["start"],
                        end_time=cue_time_to_seconds(match["time"]),
                        title=previous["title"],
                    )
                )
            previous = {"start": cue_time_to_seconds(match["time"]), "title": current_title}
    if previous:
        segments.append(
            SegmentData(
                start_time=previous["start"],
                end_time=previous["start"],
                title=previous["title"],
            )
        )
    return segments


def cue_from_segment_data(segments: Iterable[SegmentData], file_name: str = "output") -> List[str]:
    """Generate cue sheet lines from a list of segments."""
    lines = [f'FILE "{file_name}" WAVE']
    for i, segment in enumerate(segments, start=1):
        lines.append(f"  TRACK {i:02d} AUDIO")
        if segment.title:
            lines.append(f'    TITLE "{segment.title}"')
        lines.append(f"    INDEX 01 {seconds_to_cue_time(segment.start_time)}")
    return lines
