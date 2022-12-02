"""Slide command tests."""
import shutil
from unittest import mock

import pytest

import testhelpers
from m4b_util.subcommands.slide import _slide_segment_list, run
from m4b_util.helpers import SegmentData
from m4b_util.helpers.finders import find_chapters


def _run_slide_cmd(arg_list):
    """Patch the runtime arguments, then run the split command."""
    argv_patch = ["m4b-util", "slide"]
    argv_patch.extend(arg_list)

    with mock.patch("sys.argv", argv_patch):
        run()


def test_slide_forward(tmp_path, chaptered_audio_file_path):
    """Slide all chapters forward."""
    original_file = tmp_path / "original.m4b"
    shutil.copy(chaptered_audio_file_path, original_file)
    _run_slide_cmd([str(chaptered_audio_file_path), "-d", "1.0"])
    segment_list = find_chapters(chaptered_audio_file_path)
    # Remove backing file info. We aren't testing that.
    for segment in segment_list:
        segment.backing_file = None
        segment.backing_file_start_time = None
        segment.backing_file_end_time = None
    expected = [
        SegmentData(id=0, start_time=00.0, end_time=03.5, title="110Hz - Loud"),
        SegmentData(id=1, start_time=03.5, end_time=06.0, title="110Hz - Soft"),
        SegmentData(id=2, start_time=06.0, end_time=08.5, title="220Hz - Loud"),
        SegmentData(id=3, start_time=08.5, end_time=11.0, title="220Hz - Soft"),
        SegmentData(id=4, start_time=11.0, end_time=13.5, title="330Hz - Loud"),
        SegmentData(id=5, start_time=13.5, end_time=16.0, title="330Hz - Soft"),
        SegmentData(id=6, start_time=16.0, end_time=18.5, title="440Hz - Loud"),
        SegmentData(id=7, start_time=18.5, end_time=19.999, title="440Hz - Soft"),
    ]
    assert segment_list == expected


def test_slide_backward(tmp_path, chaptered_audio_file_path):
    """Slide all chapters backwards."""
    original_file = tmp_path / "original.m4b"
    shutil.copy(chaptered_audio_file_path, original_file)
    _run_slide_cmd([str(chaptered_audio_file_path), "-d", "-1.0"])
    segment_list = find_chapters(chaptered_audio_file_path)
    # Remove backing file info. We aren't testing that.
    for segment in segment_list:
        segment.backing_file = None
        segment.backing_file_start_time = None
        segment.backing_file_end_time = None
    expected = [
        SegmentData(id=0, start_time=00.0, end_time=01.5, title="110Hz - Loud"),
        SegmentData(id=1, start_time=01.5, end_time=04.0, title="110Hz - Soft"),
        SegmentData(id=2, start_time=04.0, end_time=06.5, title="220Hz - Loud"),
        SegmentData(id=3, start_time=06.5, end_time=09.0, title="220Hz - Soft"),
        SegmentData(id=4, start_time=09.0, end_time=11.5, title="330Hz - Loud"),
        SegmentData(id=5, start_time=11.5, end_time=14.0, title="330Hz - Soft"),
        SegmentData(id=6, start_time=14.0, end_time=16.5, title="440Hz - Loud"),
        SegmentData(id=7, start_time=16.5, end_time=19.999, title="440Hz - Soft"),
    ]
    assert segment_list == expected


def test_slide_segment_list_forward():
    """Shift all entries in a segment list forward, except for the final end time."""
    initial = [
        SegmentData(id=0, start_time=00.0, end_time=05.0),
        SegmentData(id=1, start_time=05.0, end_time=10.0),
        SegmentData(id=2, start_time=10.0, end_time=15.0),
        SegmentData(id=3, start_time=15.0, end_time=20.0),
    ]
    expected = [
        SegmentData(id=0, start_time=00.0, end_time=05.5),
        SegmentData(id=1, start_time=05.5, end_time=10.5),
        SegmentData(id=2, start_time=10.5, end_time=15.5),
        SegmentData(id=3, start_time=15.5, end_time=20.0),
    ]
    actual = _slide_segment_list(initial, 0.5)
    assert actual == expected


def test_slide_segment_list_backward():
    """Shift all entries in a segment list backwards, except for the initial start time."""
    initial = [
        SegmentData(id=0, start_time=00.0, end_time=05.0),
        SegmentData(id=1, start_time=05.0, end_time=10.0),
        SegmentData(id=2, start_time=10.0, end_time=15.0),
        SegmentData(id=3, start_time=15.0, end_time=20.0),
    ]
    expected = [
        SegmentData(id=0, start_time=00.0, end_time=04.5),
        SegmentData(id=1, start_time=04.5, end_time=09.5),
        SegmentData(id=2, start_time=09.5, end_time=14.5),
        SegmentData(id=3, start_time=14.5, end_time=20.0),
    ]
    actual = _slide_segment_list(initial, -0.5)
    assert actual == expected


def test_zero_segments():
    """Return immediately if presented with a zero segment list."""
    initial = []
    expected = []
    actual = _slide_segment_list(initial, 1)
    assert initial == expected == actual

    
def test_no_chapters(tmp_path, silences_file_path, capsys):
    """Alert the user if there are no chapters to slide."""
    original_file = tmp_path / "original.m4b"
    shutil.copy(silences_file_path, original_file)
    with testhelpers.expect_exit_with_output(capsys, "No chapters found"):
        _run_slide_cmd([str(silences_file_path), "-d", "-1.0"])
