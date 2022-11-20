"""Bind Command"""
import argparse
from pathlib import Path
import sys

from natsort import natsorted
from rich import print

from .Binder import Binder


def _parse_bind_args():
    """Parse all arguments."""
    parser = argparse.ArgumentParser(
        description="Take a folder of audio files and output an m4b.",
        prog="m4b-util bind"
    )
    parser.add_argument('input_folder', type=str, help="The folder of input files.")
    parser.add_argument('-a', "--author", type=str, help="Name of the author.")
    parser.add_argument('-c', "--cover", type=str, help="Image file to use as cover")
    parser.add_argument('-e', "--input-extension", type=str, action='extend', default=["mp3"], nargs="+",
                        help="Add a file extension to the allowed list used when grabbing input files, in addition "
                             "to mp3.")
    parser.add_argument('-o', "--output-dir", type=str, help="Directory to put the finished audiobook.")
    parser.add_argument('-n', "--output-name", type=str, help="Filename to use for finished audiobook. Default"
                                                              " is '[Author] - [Title].m4b'.")
    parser.add_argument('-t', "--title", type=str, help="Title of the audiobook.")
    parser.add_argument("--date", type=str, help="Date to include in metadata.")
    parser.add_argument("--decode-durations", "--decode-duration", action='store_true',
                        help="Fully decode each file to determine its duration (Slower, but more accurate).")
    parser.add_argument("--show-order", action='store_true',
                        help="Show the order the files would be read in, then exit.")
    parser.add_argument("--keep-temp-files", action='store_true', help="Skip cleanup. (Debugging)")
    parser.add_argument("--use-filename", "--use-filenames", action='store_true',
                        help="Use the filename as the chapter title instead of the title from the file's metadata.")

    return parser.parse_args(sys.argv[2:])


def run():
    """Entrypoint for bind subcommand."""
    binder = Binder()
    args = _parse_bind_args()

    # Make sure the output directory exists, if it was specified.
    if args.output_dir and not Path(args.output_dir).is_dir():
        print(f"[bold red]Error:[/] '{args.output_dir}' is not a directory.")
        return -1

    # Set info from args
    binder.author = args.author
    binder.cover = args.cover
    binder.output_dir = args.output_dir
    binder.output_name = args.output_name
    binder.title = args.title
    binder.date = args.date
    binder.decode_durations = args.decode_durations
    binder.keep_temp_files = args.keep_temp_files
    binder.use_filename = args.use_filename

    # Discover the input files
    audio_list = list()
    for ext in args.input_extension:
        # Remove leading dots, if any
        ext = ext.lstrip(".")

        # Glob them all!
        audio_list.extend(Path(args.input_folder).glob(f"*.{ext}"))
    input_files = natsorted(audio_list)

    # Print order, if applicable
    if args.show_order:
        i = 0
        for file in input_files:
            print(f"{i:3}:\t{file.name}")
            i += 1
        return 0

    # Add the files to the binder
    binder.files = input_files

    # Run the binder
    if binder.bind():
        # Tell the user where it is.
        print(f"[cyan]Writing '[yellow]{binder.output_path}[/]'")

    return 0
