import argparse
from pathlib import Path
import sys

from rich import print

from ..helpers import Audiobook
from ..helpers.finders import find_chapters


def _parse_args():
    parser = argparse.ArgumentParser(
        prog="m4b-util slide",
        description='Slide chapter segments up or down.'
    )
    parser.add_argument('input_file', help='Input filename')
    parser.add_argument('-d', "--duration", type=float, help='Duration to shift (seconds). Negative values allowed.')

    return parser.parse_args(sys.argv[2:])


def _slide_segment_list(segments, duration):
    """Slide all segments in a list in the indicated direction. Will not overshoot final or initial values."""
    if len(segments) == 0:
        return segments # No values, so no slide
    start_time = segments[0].start_time
    end_time = segments[-1].end_time
    duration = float(duration)
    for segment in segments:
        segment.start_time = segment.start_time + duration
        segment.end_time = segment.end_time + duration
    # Restore original start and end times.
    segments[-1].end_time = end_time
    segments[0].start_time = start_time

    return segments


def run():
    """Split an audio file into pieces, based on silence."""
    args = _parse_args()
    input_path = Path(args.input_file)
    book = Audiobook()
    book.add_chapters_from_chaptered_file(input_path)
    if book.chapters:
        book.chapters = _slide_segment_list(book.chapters, args.duration)
        book.bind(input_path)
        print(f"Chapters slid by {args.duration}")
    else:
        print("[red]Error:[/] No chapters found!")
        exit(1)


