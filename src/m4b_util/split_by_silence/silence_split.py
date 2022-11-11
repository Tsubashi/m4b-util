import argparse
from pathlib import Path
import re
import sys

from rich import print

from ..helpers import ffprogress
from ..helpers.ParallelFFmpeg import ParallelFFmpeg


def _parse_split_silence_args():
    parser = argparse.ArgumentParser(description='Split media into separate chunks wherever silence occurs')
    parser.add_argument('input_file', help='Input filename (`-` for stdin)')
    parser.add_argument('-o', "--output-dir", type=str, help="Directory to place output.")
    parser.add_argument('-p', '--output-pattern', type=str, default="segment_{:04d}.mp3",
                        help='Output filename pattern (e.g. `segment_{:04d}.mp3`)')
    parser.add_argument('-t', "--silence-threshold", default=-35, type=int, help='Silence threshold (in dB)')
    parser.add_argument('-d', "--silence-duration", default=3.0, type=float, help='Silence duration')
    parser.add_argument('-s', "--start-time", type=float, help='Start time (seconds)')
    parser.add_argument('-e', "--end-time", type=float, help='End time (seconds)')

    return parser.parse_args(sys.argv[2:])


silence_start_re = re.compile(r' silence_start: (?P<start>[0-9]+(\.?[0-9]*))$')
silence_end_re = re.compile(r' silence_end: (?P<end>[0-9]+(\.?[0-9]*)) ')
total_duration_re = re.compile(
    r'size=[^ ]+ time=(?P<hours>[0-9]{2}):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9\.]{5}) bitrate=')


def _get_segment_times(start_time, lines):
    # Chunks start when silence ends, and chunks end when silence starts.
    segment_starts = []
    segment_ends = []
    end_time = 10000000.0
    for line in lines:
        # Check for silence start
        silence_start_match = silence_start_re.search(line)
        if silence_start_match:
            segment_ends.append(float(silence_start_match.group('start')))
            if len(segment_starts) == 0:
                # Started with non-silence.
                segment_starts.append(start_time or 0.)
            continue

        # Check for silence end
        silence_end_match = silence_end_re.search(line)
        if silence_end_match:
            segment_starts.append(float(silence_end_match.group('end')))
        total_duration_match = total_duration_re.search(line)

        # Check for duration
        if total_duration_match:
            hours = int(total_duration_match.group('hours'))
            minutes = int(total_duration_match.group('minutes'))
            seconds = float(total_duration_match.group('seconds'))
            end_time = hours * 3600 + minutes * 60 + seconds

    if len(segment_starts) == 0:
        # No silence found.
        segment_starts.append(start_time)

    if len(segment_starts) > len(segment_ends):
        # Finished with non-silence.
        segment_ends.append(end_time)

    output = list(zip(segment_starts, segment_ends))

    # Remove any segments less than 1 second
    # Use .copy() so that we can modify the original without throwing off the iterator
    for start, end in output.copy():
        if end - start < 1.0:
            output.remove((start, end))

    return output


def split_audio():
    """Split an audio file into pieces, based on silence."""
    args = _parse_split_silence_args()

    # Run ffmpeg's silencedetect filter
    cmd = ["ffmpeg", "-i", args.input_file]
    if args.start_time:
        cmd.extend(["-ss", str(args.start_time)])
    else:
        args.start_time = 0.
    if args.end_time:
        cmd.extend(["-to", str(args.end_time)])
    cmd.extend([
        "-filter_complex",
        f"[0]silencedetect=d={args.silence_duration}:n={args.silence_threshold}dB[s0]",
        "-map", "[s0]",
        "-f", "null",
        "-"
    ])
    ff = ffprogress.run(cmd, "Detecting Silence")

    # Check to see if ffmpeg exited abnormally
    if ff is None:
        print("[bold red]Error:[/] Could not determine segment times.")
        exit(1)
    lines = ff.output.splitlines()

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
