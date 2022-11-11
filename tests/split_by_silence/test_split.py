"""Test Split-by-silence."""
from contextlib import contextmanager
import os
from pathlib import Path
from unittest import mock

import pytest

from m4b_util.helpers import ffprobe
from m4b_util.split_by_silence import split


@contextmanager
def change_cwd(new_path):
    """Change to a new directory, then change back when finished."""
    owd = Path.cwd()  # Original Working Directory
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(owd)


def _run_split_cmd(arg_list):
    """Patch the runtime arguments, then run the split command."""
    argv_patch = ["m4b-util", "split-by-silence"]
    argv_patch.extend(arg_list)

    with mock.patch("sys.argv", argv_patch):
        split.split_audio()


def _run_and_check_output(cmd_args, output_path, expected_files=None, check_func=None):
    """Run the split command and check that expected output exists.

    :param cmd_args: List of arguments to use to patch argv, as though called on a command line.
    :param output_path: Path to the directory to check.
    :param expected_files: Files we expect to find in output_path. If unspecified, defaults to ["segment_0000.mp3"].
    :param check_func: Function for checking each file in expected_files. Defaults to asserting ffprobe can read them.

    """
    def default_check(input_file):
        probe = ffprobe.run_probe(input_file)
        # Add the file name so the error is more readable if the test fails.
        assert input_file.name and probe

    if not expected_files:
        expected_files = ["segment_0000.mp3"]
    if not check_func:
        check_func = default_check
    _run_split_cmd(cmd_args)
    for file_name in expected_files:
        file_path = output_path / file_name
        check_func(file_path)

    # Make sure there aren't any other files in the directory other than the filelist
    for file in output_path.glob("*"):
        assert (file.name in expected_files)


def test_get_segment_times():
    """Extract segment times from ffmpeg output."""
    lines = [
        "[silencedetect @ 0x12860aa70] silence_start: 2.5000",
        "size=N/A time=00:00:25.00 bitrate=N/A speed= 836x",
        "[silencedetect @ 0x12860aa70] silence_end: 5.0000 | silence_duration: 2.5000",
        "[silencedetect @ 0x12860aa70] silence_start: 7.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 10.000 | silence_duration: 2.5000",
        "[silencedetect @ 0x12860aa70] silence_start: 12.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 15.0000 | silence_duration: 2.5000",
        "[silencedetect @ 0x12860aa70] silence_start: 17.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 20.000 | silence_duration: 2.5000",
    ]
    expected = [(0.0, 2.5), (5.0, 7.5), (10.0, 12.5), (15.0, 17.5), (20.0, 25.0)]
    assert split._get_segment_times(0, lines) == expected


def test_get_segment_times_non_zero_start_time():
    """Extract segment times from ffmpeg output, starting at a non-zero time."""
    lines = [
        "[silencedetect @ 0x12860aa70] silence_end: 5.0000 | silence_duration: 2.5000",
        "size=N/A time=00:00:25.00 bitrate=N/A speed= 836x",
        "[silencedetect @ 0x12860aa70] silence_start: 7.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 10.000 | silence_duration: 2.5000",
        "[silencedetect @ 0x12860aa70] silence_start: 12.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 15.0000 | silence_duration: 2.5000",
        "[silencedetect @ 0x12860aa70] silence_start: 17.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 20.000 | silence_duration: 2.5000",
    ]
    expected = [(5.0, 7.5), (10.0, 12.5), (15.0, 17.5), (20.0, 25.0)]
    assert split._get_segment_times(1.25, lines) == expected


def test_get_segment_times_detect_end_first():
    """Handle segment times even if silence_end comes first."""
    lines = [
        "[silencedetect @ 0x12860aa70] silence_end: 5.0000 | silence_duration: 2.5000",
        "size=N/A time=00:00:25.00 bitrate=N/A speed= 836x",
        "[silencedetect @ 0x12860aa70] silence_start: 7.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 10.000 | silence_duration: 2.5000",
        "[silencedetect @ 0x12860aa70] silence_start: 12.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 15.0000 | silence_duration: 2.5000",
        "[silencedetect @ 0x12860aa70] silence_start: 17.5000",
        "[silencedetect @ 0x12860aa70] silence_end: 20.000 | silence_duration: 2.5000",
    ]
    expected = [(5.0, 7.5), (10.0, 12.5), (15.0, 17.5), (20.0, 25.0)]
    assert split._get_segment_times(1.25, lines) == expected


def test_get_segment_times_empty():
    """Notice when we don't have any silence to extract."""
    expected = [(0.0, 10000000.0)]
    assert split._get_segment_times(0, [""]) == expected


def test_split_audio(tmp_path, silences_file_path):
    """Split a file, default settings."""
    output_path = tmp_path / "output"
    output_path.mkdir()
    with change_cwd(output_path):
        _run_and_check_output([str(silences_file_path)], output_path)


def test_split_audio_set_outdir(tmp_path, silences_file_path):
    """Split a file, setting the output directory."""
    output_path = tmp_path / "output"
    _run_and_check_output([str(silences_file_path), "-o", str(output_path)], output_path)


def test_split_audio_start_end_times(tmp_path, silences_file_path):
    """Split a file, with start and end times specified."""
    output_path = tmp_path / "output"
    _run_and_check_output(
        cmd_args=[
            str(silences_file_path),
            "-o", str(output_path),
            "-s", "1.75",
            "-e", "5.03"
        ],
        output_path=output_path,
        expected_files={"segment_0000.mp3": "bf0e18da559fcaba399a789f7542f6a9a59d947e"}
    )


def test_split_audio_fail(tmp_path, capsys):
    """Exit with non-zero code when asked to process a non-audio file."""
    fake_file_path = tmp_path / "not-a-real-file.m4a"
    open(fake_file_path, 'a').close()
    with pytest.raises(SystemExit) as e:
        _run_split_cmd([str(fake_file_path), "-o", str(tmp_path)])
    assert (e.value.code == 1)
    output = capsys.readouterr()
    assert "Could not determine segment times." in output.out


def test_split_audio_duration(tmp_path, silences_file_path):
    """Adjust silence duration limits."""
    output_path = tmp_path / "output"
    cmd = [
        str(silences_file_path),
        "-o", str(output_path),
        "-d", "1.5"
    ]
    expected_files = (
        "segment_0000.mp3",
        "segment_0001.mp3",
        "segment_0002.mp3",
        "segment_0003.mp3",
    )
    _run_and_check_output(cmd, output_path, expected_files)


def test_split_audio_threshold_lower(tmp_path, variable_volume_segments_file_path):
    """Adjust silence threshold limits to a threshold lower than any noise in the file."""
    output_path = tmp_path / "output"

    # Start with a threshold lower than any noise in the file. This should give us two empty files
    cmd = [
        str(variable_volume_segments_file_path),
        "-o", str(output_path),
        "-t", "-45",
        "-d", "1.5"
    ]
    _run_and_check_output(cmd, output_path)


def test_split_audio_threshold_higher(tmp_path, variable_volume_segments_file_path, capsys):
    """Adjust silence threshold limits to a threshold higher than any noise in the file."""
    output_path = tmp_path / "output"
    cmd = [
        str(variable_volume_segments_file_path),
        "-o", str(output_path),
        "-t", "-5",
        "-d", "1.5"
    ]
    with pytest.raises(SystemExit) as e:
        _run_split_cmd(cmd)
    assert (e.value.code == 1)
    output = capsys.readouterr()
    assert "No silence found." in output.out


def test_split_audio_threshold(tmp_path, variable_volume_segments_file_path):
    """Adjust silence threshold limits to a threshold right between the two volume levels in the file."""
    output_path = tmp_path / "output"
    cmd = [
        str(variable_volume_segments_file_path),
        "-o", str(output_path),
        "-t", "-20",
        "-d", "1.5"
    ]
    expected_files = (
        "segment_0000.mp3",
        "segment_0001.mp3",
        "segment_0002.mp3",
        "segment_0003.mp3",
    )
    _run_and_check_output(cmd, output_path, expected_files)


def test_split_audio_segment_pattern(tmp_path, silences_file_path):
    """Specify a non-default segment pattern."""
    output_path = tmp_path / "output"
    cmd = [
        str(silences_file_path),
        "-o", str(output_path),
        "-d", "1.5",
        "-p", "chunk_{:02d}.mp3",
    ]
    # Make sure the files we expect are there
    expected_files = (
        "chunk_00.mp3",
        "chunk_01.mp3",
        "chunk_02.mp3",
        "chunk_03.mp3",
    )
    _run_and_check_output(cmd, output_path, expected_files)
