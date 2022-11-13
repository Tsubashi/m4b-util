import argparse
from pathlib import Path
import sys

from rich import print

from ..helpers import ffprogress
from ..helpers.ParallelFFmpeg import ParallelFFmpeg


def _parse_split_silence_args():
    parser = argparse.ArgumentParser(description='Split media into segments')
    parser.add_argument('mode', help='Options: Silence, Chapters')
    parser.add_argument('input_file', help='Input filename')
    parser.add_argument('-o', "--output-dir", type=str, help="Directory to place output.")
    parser.add_argument('-p', '--output-pattern', type=str, default="segment_{:04d}.mp3",
                        help='Output filename pattern (e.g. `segment_{:04d}.mp3`)')
    parser.add_argument('-t', "--silence-threshold", default=-35, type=int, help='Silence threshold (in dB)')
    parser.add_argument('-d', "--silence-duration", default=3.0, type=float, help='Silence duration')
    parser.add_argument('-s', "--start-time", type=float, help='Start time (seconds)')
    parser.add_argument('-e', "--end-time", type=float, help='End time (seconds)')

    return parser.parse_args(sys.argv[2:])


def run():
    """Split an audio file into pieces, based on silence."""
    args = _parse_split_silence_args()



    # Parse the segments from ffmpeg output
    segment_times = _get_segment_times(args.start_time, lines)
    if not segment_times:
        print("[bold red]Error:[/] No silence found.")
        exit(1)

    # Generate task list
    tasks = list()
    input_path = Path(args.input_file)
    for i, (start_time, end_time) in enumerate(segment_times):
        time = end_time - start_time
        if args.output_dir:
            output_path = Path(args.output_dir)
        else:
            output_path = Path()
        output_path.mkdir(exist_ok=True)
        output_path = output_path / args.output_pattern.format(i, i=i)

        cmd = ["ffmpeg", "-i", input_path, "-ss", str(start_time), "-t", str(time), "-y", output_path]
        name = f"Splitting segment {i}"
        tasks.append({
            "name": name,
            "command": cmd
        })

    # Process splits in parallel
    print(f"[yellow]Info:[/] Found [yellow]{len(tasks)}[/] segments")
    p = ParallelFFmpeg(f"Splitting '{input_path.name}'")
    p.process(tasks)
