# Standard Library
import argparse
from pathlib import Path
import re
import sys

# Third Party
from lark import UnexpectedInput
from rich import print

# Local
from ..helpers import Audiobook, ffprobe, SegmentData
from ..helpers.ffmetadata import FFMETADATA_TERMINATOR_FRIENDLY_NAMES


def _parse_args():
    parser = argparse.ArgumentParser(
        prog="m4b-util load-labels",
        description="Convert between audacity labels and ffmpeg chapter metadata."
    )
    # Inputs
    input_options = parser.add_mutually_exclusive_group(required=True)
    input_options.add_argument("--from-book", help="Read chapters from file.")
    input_options.add_argument("--from-label-file", help="Read audacity labels from text file.")
    input_options.add_argument("--from-metadata-file", help="Read ffmpeg metadata from file.")

    # Outputs
    output_options = parser.add_argument_group("output options")
    output_options.add_argument("--to-metadata-file", type=str, help="Output ffmpeg metadata to file.")
    output_options.add_argument("--to-label-file", type=str, help="Output labels to file.")
    output_options.add_argument("--to-book", type=str, help="Apply labels as chapters to existing book file.")

    args = parser.parse_args(sys.argv[2:])
    return args


def segment_data_from_labels(labels):
    """Read labels from a file and fill a segment data list.

    :param labels: A list of labels lines, preferably from running readlines() on a label file.
    :returns: A list of SegmentData
    """
    segments = list()
    label_regex = re.compile(r"^(?P<start_time>\d+\.?\d*)\s+(?P<end_time>\d+\.?\d*)\s+(?P<title>.*)\s*$")
    previous = None
    for label in labels:
        match = label_regex.search(label)
        if match:
            if previous:
                segments.append(
                    SegmentData(
                        start_time=previous['start_time'],
                        end_time=float(match['start_time']),
                        title=previous['title'])
                )
            previous = {
                "start_time": float(match['start_time']),
                "end_time": float(match['end_time']),
                "title": match['title']
            }
        else:
            print(f"[orange]Warning:[/] Could not parse label: '{label}'")

    # Make sure to hande the final label
    segments.append(SegmentData(
        start_time=previous['start_time'],
        end_time=previous['end_time'],
        title=previous['title']
    ))

    return segments


def labels_from_segment_data(segments):
    """Generate labels from a segment data list."""
    labels = list()
    for segment in segments:
        labels.append(f"{segment.start_time}\t{segment.start_time}\t{segment.title}")
    return labels


def _handle_input(args, book):
    # Handle input
    if args.from_label_file:
        with open(args.from_label_file) as f:
            labels = f.readlines()
        book.chapters = segment_data_from_labels(labels)
    elif args.from_book:
        book.add_chapters_from_chaptered_file(args.from_book)
    else:  # args.from_metadata_file:
        with open(args.from_metadata_file) as f:
            metadata = f.read()
            try:
                book.metadata = metadata
            except UnexpectedInput as e:
                print(f"[red]Error:[/] Parsing metadata failed on line {e.line}, column {e.column}:")
                print(f"{e.get_context(metadata)}")
                print("Expected one of the following token types:")
                for terminator in e.accepts:
                    print(f" - {FFMETADATA_TERMINATOR_FRIENDLY_NAMES.get(terminator, terminator)}")
                return False
    return True


def _handle_output(args, book):
    if args.to_label_file:
        with open(args.to_label_file, 'w') as f:
            for label in labels_from_segment_data(book.chapters):
                f.write(f"{label}\n")
    if args.to_metadata_file:
        with open(args.to_metadata_file, 'w') as f:
            f.write(book.metadata)
    if args.to_book:
        new_book = Audiobook()
        new_book.add_chapters_from_chaptered_file(args.to_book)
        new_book_dur = ffprobe.get_file_duration(args.to_book)
        new_chapters = list()
        for chapter in book.chapters:
            # Check to see if a chapter is straddling the cutoff. If so, set the chapter's end equal to the cutoff.
            if chapter.end_time > new_book_dur > chapter.start_time:
                chapter.end_time = new_book_dur

            # Only add chapters that are within the new books bounds
            if chapter.end_time <= new_book_dur:
                new_chapters.append(
                    SegmentData(
                        start_time=chapter.start_time,
                        end_time=chapter.end_time,
                        title=chapter.title,
                        backing_file=Path(args.to_book),
                        file_start_time=chapter.start_time,
                        file_end_time=chapter.end_time
                    )
                )
        new_book.chapters = new_chapters
        new_book.bind(args.to_book)


def run():
    """Run the subcommand."""
    # Set up variables
    args = _parse_args()
    book = Audiobook()

    # Handle input
    if not _handle_input(args, book):
        return 1

    # Handle output
    _handle_output(args, book)
