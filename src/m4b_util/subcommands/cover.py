import argparse
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory


from m4b_util.helpers import cover_utils


def _parse_args():
    parser = argparse.ArgumentParser(
        prog="m4b-util cover",
        description='Manipulate Covers.'
    )
    parser.add_argument('input_file', type=str, help='Input filename')

    parser.add_argument('-e', "--extract-cover", type=str,
                        help='Extract existing cover from input. Must end in .png or .jpg')
    parser.add_argument('-a', "--apply-cover", type=str, help='Apply specified cover to input file.')
    args = parser.parse_args(sys.argv[2:])
    if not (args.extract_cover or args.apply_cover):
        parser.error("At least one task must be specified (--extract-cover or --apply-cover).")
    return args


def run():
    """Do stuff with a cover."""
    args = _parse_args()
    if args.extract_cover:
        cover_utils.extract_cover(Path(args.input_file), Path(args.extract_cover))
    if args.apply_cover:
        with TemporaryDirectory() as tmp_path:
            covered_book = Path(tmp_path) / "covered.m4b"
            cover_utils.add_cover(Path(args.input_file), Path(args.apply_cover), covered_book)
            shutil.move(covered_book, args.input_file)
