import argparse
from pathlib import Path
import sys

from rich import print

from ..helpers import Audiobook


def _parse_args():
    parser = argparse.ArgumentParser(
        prog="m4b-util slide",
        description='Slide chapter segments up or down.'
    )
    parser.add_argument('input_file', help='Input filename')
    parser.add_argument('-d', "--duration", type=float, help='Duration to shift (seconds). Negative values allowed.')
    parser.add_argument("--trim-start", type=float, help='Duration to trim from beginning (seconds).')

    return parser.parse_args(sys.argv[2:])


def _slide(segments, duration):
    """Add duration to all relevant fields each segment."""
    for segment in segments:
        segment.start_time = segment.start_time + duration
        segment.end_time = segment.end_time + duration
        if segment.file_start_time is not None:
            segment.file_start_time = segment.file_start_time + duration
        if segment.file_end_time is not None:
            segment.file_end_time = segment.file_end_time + duration


def _check_overshoot(segments, start_time, end_time, file_start_time, file_end_time):
    """Remove any segments that exist outside the start and end time."""
    for segment in segments.copy():
        if segment.start_time > end_time \
                or segment.end_time <= 0 \
                or segment.end_time < start_time:
            segments.remove(segment)
            continue
        # Don't do any operations on backing_file info if one of the needed vars is None.
        if None not in (segment.file_start_time, segment.file_end_time, file_start_time, file_end_time):
            if segment.file_start_time > file_end_time \
                    or segment.file_end_time <= 0 \
                    or segment.file_end_time < file_start_time:
                segments.remove(segment)


def _slide_segments(segments, duration):
    """Slide all segments in a list in the indicated direction. Will not overshoot final or initial values.

    :param segments: List of segments to slide.
    :param duration: How far to slide the segments.
    :return: List of segments, slid by duration.
    """
    # Check preconditions
    if len(segments) == 0:
        return segments  # No values, so no slide
    if duration == 0:
        return segments  # No slide duration, no slide needed

    # Set initial state
    start_time = segments[0].start_time
    end_time = segments[-1].end_time
    duration = float(duration)
    file_start_time = segments[0].file_start_time
    file_end_time = segments[-1].file_end_time

    # Slide all segments
    _slide(segments, duration)

    # Check for overshoot
    original_length = len(segments)
    _check_overshoot(segments, start_time, end_time, file_start_time, file_end_time)

    # Renumber segments, if applicable
    if len(segments) != original_length:
        for i, segment in enumerate(segments):
            segment.id = i

    # Restore original start and end times, if we have any segments left.
    if segments:
        segments[-1].end_time = end_time
        segments[0].start_time = start_time
        # These will be None if unset
        segments[-1].file_end_time = file_end_time
        segments[0].file_start_time = file_start_time

    return segments


def run():
    """Split an audio file into pieces, based on silence."""
    args = _parse_args()
    input_path = Path(args.input_file)
    slide_dur = 0
    if args.duration:
        slide_dur = args.duration
    if args.trim_start:
        slide_dur = slide_dur - args.trim_start

    book = Audiobook()
    book.add_chapters_from_chaptered_file(input_path)
    if book.chapters:
        # Find initial end times, in case we need to modify it.
        end_time = book.chapters[-1].end_time
        file_end_time = book.chapters[-1].file_end_time

        if args.trim_start:
            # Remove chapters smaller than our trim value
            # Use .copy so that we can delete from the original without screwing up the iterator
            for chapter in book.chapters.copy():
                if chapter.end_time < args.trim_start:
                    book.chapters.remove(chapter)
                else:
                    break
            if not book.chapters:
                print("[bold red]Error:[/] No chapters were left after trim.")
                exit(1)
            # Set expected start and end times, since the slide function won't touch those
            book.chapters[0].start_time = 0.0
            book.chapters[0].file_start_time = 0.0
            book.chapters[-1].end_time = end_time - args.trim_start
            book.chapters[-1].file_end_time = file_end_time - args.trim_start

        # Slide any remaining chapters
        book.chapters = _slide_segments(book.chapters, slide_dur)
        if not book.chapters:
            print("[bold red]Error:[/] No chapters were left after slide.")
            exit(1)

        # Write our new file
        if book.bind(input_path) is False:  # pragma: nocover - failures here aren't likely the fault of this module
            exit(1)
        print(f"Chapters slid by {args.duration}")
        return 0

    else:
        print("[red]Error:[/] No chapters found!")
        exit(1)
