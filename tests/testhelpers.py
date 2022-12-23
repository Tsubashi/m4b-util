from contextlib import contextmanager
from pathlib import Path

import pytest

from m4b_util.helpers import ffprobe


def check_output_folder(output_path, expected_files=None, check_func=None):
    """Check that expected output exists.

    :param output_path: Path to the directory to check.
    :param expected_files: Files we expect to find in output_path. If unspecified, defaults to ["segment_0000.mp3"].
    :param check_func: Function for checking each file in expected_files. Defaults to asserting ffprobe can read them.

    """
    # Default check function, in case one isn't passed in.
    def default_check(input_file_path):
        """Ensure ffprobe can read the file."""
        # Add in filename to make any failure more legible
        assert input_file_path.name and ffprobe.run_probe(input_file_path)

    # Set defaults
    if expected_files is None:
        expected_files = ["segment_0000.mp3"]
    if not check_func:
        check_func = default_check

    # Check the output
    for file_name in expected_files:
        file_path = output_path / file_name
        check_func(file_path)

    # Make sure there aren't any extra files in the directory
    for file in output_path.glob("*"):
        assert (file.name in expected_files)


def assert_file_path_is_file(input_file_path):
    """Ensure each file exists and is a file."""
    assert input_file_path.is_file()


def soften_backing_file(segment_list):
    """Remove path portion of backing_file from segments, as it will change with each test."""
    for segment in segment_list:
        segment.backing_file = Path(segment.backing_file.stem)


@contextmanager
def expect_exit(expected_code=1):
    """Ensure a function exits, and writes an expected string to stdout or stderr."""
    with pytest.raises(SystemExit) as e:
        yield
    assert e.value.code == expected_code


@contextmanager
def expect_exit_with_output(capsys, expected_text, expected_code=1):
    """Ensure a function exits, and writes an expected string to stdout or stderr."""
    with expect_exit(expected_code):
        yield
    output = capsys.readouterr()
    assert (expected_text in output.out) or (expected_text in output.err)
