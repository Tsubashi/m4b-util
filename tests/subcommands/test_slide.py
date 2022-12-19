"""Slide command tests."""
import shutil
from unittest import mock

import testhelpers

from m4b_util.helpers import SegmentData
from m4b_util.helpers.finders import find_chapters
from m4b_util.subcommands import slide


def _slide_and_check_segments(arg_list, input_path, expected_segments):
    """Run the split command, find chapters in the output, and check against what we expect."""
    _run_slide_cmd(arg_list)
    segment_list = find_chapters(input_path)
    # Remove backing file info. We aren't testing that.
    for segment in segment_list:
        segment.backing_file = None
    assert segment_list == expected_segments


def _run_slide_cmd(arg_list):
    """Patch the runtime arguments, then run the split command."""
    argv_patch = ["m4b-util", "slide"]
    argv_patch.extend(arg_list)

    with mock.patch("sys.argv", argv_patch):
        slide.run()


def test_slide_forward(tmp_path, chaptered_audio_file_path):
    """Slide all chapters forward."""
    cmd = [str(chaptered_audio_file_path), "-d", "1.0"]
    expected = [
        SegmentData(id=0, title="110Hz - Loud",
                    start_time=00.0, file_start_time=00.0,
                    end_time=03.5, file_end_time=03.5),
        SegmentData(id=1, title="110Hz - Soft",
                    start_time=03.5, file_start_time=03.5,
                    end_time=06.0, file_end_time=06.0),
        SegmentData(id=2, title="220Hz - Loud",
                    start_time=06.0, file_start_time=06.0,
                    end_time=08.5, file_end_time=08.5),
        SegmentData(id=3, title="220Hz - Soft",
                    start_time=08.5, file_start_time=08.5,
                    end_time=11.0, file_end_time=11.0),
        SegmentData(id=4, title="330Hz - Loud",
                    start_time=11.0, file_start_time=11.0,
                    end_time=13.5, file_end_time=13.5),
        SegmentData(id=5, title="330Hz - Soft",
                    start_time=13.5, file_start_time=13.5,
                    end_time=16.0, file_end_time=16.0),
        SegmentData(id=6, title="440Hz - Loud",
                    start_time=16.0, file_start_time=16.0,
                    end_time=18.5, file_end_time=18.5),
        SegmentData(id=7, title="440Hz - Soft",
                    start_time=18.5, file_start_time=18.5,
                    end_time=19.999, file_end_time=19.999),
    ]
    _slide_and_check_segments(cmd, chaptered_audio_file_path, expected)


def test_slide_backward(tmp_path, chaptered_audio_file_path):
    """Slide all chapters backwards, preserving start and end times."""
    cmd = [str(chaptered_audio_file_path), "-d", "-1.0"]
    expected = [
        SegmentData(id=0, title="110Hz - Loud",
                    start_time=00.0, file_start_time=00.0,
                    end_time=01.5, file_end_time=01.5),
        SegmentData(id=1, title="110Hz - Soft",
                    start_time=01.5, file_start_time=01.5,
                    end_time=04.0, file_end_time=04.0),
        SegmentData(id=2, title="220Hz - Loud",
                    start_time=04.0, file_start_time=04.0,
                    end_time=06.5, file_end_time=06.5),
        SegmentData(id=3, title="220Hz - Soft",
                    start_time=06.5, file_start_time=06.5,
                    end_time=09.0, file_end_time=09.0),
        SegmentData(id=4, title="330Hz - Loud",
                    start_time=09.0, file_start_time=09.0,
                    end_time=11.5, file_end_time=11.5),
        SegmentData(id=5, title="330Hz - Soft",
                    start_time=11.5, file_start_time=11.5,
                    end_time=14.0, file_end_time=14.0),
        SegmentData(id=6, title="440Hz - Loud",
                    start_time=14.0, file_start_time=14.0,
                    end_time=16.5, file_end_time=16.5),
        SegmentData(id=7, title="440Hz - Soft",
                    start_time=16.5, file_start_time=16.5,
                    end_time=19.999, file_end_time=19.999),
    ]
    _slide_and_check_segments(cmd, chaptered_audio_file_path, expected)


def test_slide_segment_list_forward():
    """Shift all entries in a segment list forward, preserving start and end times."""
    initial = [
        SegmentData(id=0,
                    start_time=00.0, file_start_time=00.0,
                    end_time=05.0, file_end_time=05.0),
        SegmentData(id=1,
                    start_time=05.0, file_start_time=05.0,
                    end_time=10.0, file_end_time=10.0),
        SegmentData(id=2,
                    start_time=10.0, file_start_time=10.0,
                    end_time=15.0, file_end_time=15.0),
        SegmentData(id=3,
                    start_time=15.0, file_start_time=15.0,
                    end_time=20.0, file_end_time=20.0),
    ]
    expected = [
        SegmentData(id=0,
                    start_time=00.0, file_start_time=00.0,
                    end_time=05.5, file_end_time=05.5),
        SegmentData(id=1,
                    start_time=05.5, file_start_time=05.5,
                    end_time=10.5, file_end_time=10.5),
        SegmentData(id=2,
                    start_time=10.5, file_start_time=10.5,
                    end_time=15.5, file_end_time=15.5),
        SegmentData(id=3,
                    start_time=15.5, file_start_time=15.5,
                    end_time=20.0, file_end_time=20.0),
    ]
    actual = slide._slide_segments(initial, 0.5)
    assert actual == expected


def test_overshoot_backing_only():
    """Overshoot backing file times."""
    initial = [
        SegmentData(id=0,
                    start_time=00.0, file_start_time=00.0,
                    end_time=05.0, file_end_time=05.0),
        SegmentData(id=1,
                    start_time=05.0, file_start_time=05.0,
                    end_time=10.0, file_end_time=10.0),
        SegmentData(id=2,
                    start_time=10.0, file_start_time=10.0,
                    end_time=15.0, file_end_time=15.0),
        SegmentData(id=3,
                    start_time=15.0, file_start_time=15.0,
                    end_time=20.0, file_end_time=17.5),
    ]
    expected = [
        SegmentData(id=0,
                    start_time=00.0, file_start_time=00.0,
                    end_time=07.6, file_end_time=07.6),
        SegmentData(id=1,
                    start_time=07.6, file_start_time=07.6,
                    end_time=12.6, file_end_time=12.6),
        SegmentData(id=2,
                    start_time=12.6, file_start_time=12.6,
                    end_time=20.0, file_end_time=17.5),
    ]
    actual = slide._slide_segments(initial, 2.6)
    assert actual == expected


def test_slide_segment_list_backward():
    """Shift all entries in a segment list backwards, except for the initial start time."""
    initial = [
        SegmentData(id=0,
                    start_time=00.0, file_start_time=00.0,
                    end_time=05.0, file_end_time=05.0),
        SegmentData(id=1,
                    start_time=05.0, file_start_time=05.0,
                    end_time=10.0, file_end_time=10.0),
        SegmentData(id=2,
                    start_time=10.0, file_start_time=10.0,
                    end_time=15.0, file_end_time=15.0),
        SegmentData(id=3,
                    start_time=15.0, file_start_time=15.0,
                    end_time=20.0, file_end_time=20.0),
    ]
    expected = [
        SegmentData(id=0,
                    start_time=00.0, file_start_time=00.0,
                    end_time=04.5, file_end_time=04.5),
        SegmentData(id=1,
                    start_time=04.5, file_start_time=04.5,
                    end_time=09.5, file_end_time=09.5),
        SegmentData(id=2,
                    start_time=09.5, file_start_time=09.5,
                    end_time=14.5, file_end_time=14.5),
        SegmentData(id=3,
                    start_time=14.5, file_start_time=14.5,
                    end_time=20.0, file_end_time=20.0),
    ]
    actual = slide._slide_segments(initial, -0.5)
    assert actual == expected


def test_slide_segments_no_backing():
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
    actual = slide._slide_segments(initial, 0.5)
    assert actual == expected


def test_zero_segments():
    """Return immediately if presented with a zero segment list."""
    initial = []
    expected = []
    actual = slide._slide_segments(initial, 1)
    assert initial == expected == actual


def test_zero_slide_duration():
    """Return immediately if presented with a zero slide durationn."""
    initial = ["Not-a-val"]
    expected = ["Not-a-val"]
    actual = slide._slide_segments(initial, 0)
    assert initial == expected == actual


def test_no_chapters(tmp_path, silences_file_path, capsys):
    """Alert the user if there are no chapters to slide."""
    original_file = tmp_path / "original.m4b"
    shutil.copy(silences_file_path, original_file)
    with testhelpers.expect_exit_with_output(capsys, "No chapters found"):
        _run_slide_cmd([str(silences_file_path), "-d", "-1.0"])


def test_trim_start(tmp_path, chaptered_audio_file_path):
    """Trim a length from the beginning of a file."""
    cmd = [str(chaptered_audio_file_path), "--trim-start", "3.6"]
    expected = [
        SegmentData(id=0, title="110Hz - Soft",
                    start_time=00.0, file_start_time=00.0,
                    end_time=01.4, file_end_time=01.4),
        SegmentData(id=1, title="220Hz - Loud",
                    start_time=01.4, file_start_time=01.4,
                    end_time=03.9, file_end_time=03.9),
        SegmentData(id=2, title="220Hz - Soft",
                    start_time=03.9, file_start_time=03.9,
                    end_time=06.4, file_end_time=06.4),
        SegmentData(id=3, title="330Hz - Loud",
                    start_time=06.4, file_start_time=06.4,
                    end_time=08.9, file_end_time=08.9),
        SegmentData(id=4, title="330Hz - Soft",
                    start_time=08.9, file_start_time=08.9,
                    end_time=11.4, file_end_time=11.4),
        SegmentData(id=5, title="440Hz - Loud",
                    start_time=11.4, file_start_time=11.4,
                    end_time=13.9, file_end_time=13.9),
        SegmentData(id=6, title="440Hz - Soft",
                    start_time=13.9, file_start_time=13.9,
                    end_time=16.399, file_end_time=16.399),
    ]
    _slide_and_check_segments(cmd, chaptered_audio_file_path, expected)


def test_trim_too_much(tmp_path, chaptered_audio_file_path, capsys):
    """Warn the user if they try to trim more off the start than is in the file."""
    original_file = tmp_path / "original.m4b"
    shutil.copy(chaptered_audio_file_path, original_file)
    with testhelpers.expect_exit_with_output(capsys, "No chapters were left after trim."):
        _run_slide_cmd([str(chaptered_audio_file_path), "--trim-start", "50.0"])


def test_slide_too_much(tmp_path, chaptered_audio_file_path, capsys):
    """Warn the user if they try to trim more off the start than is in the file."""
    original_file = tmp_path / "original.m4b"
    shutil.copy(chaptered_audio_file_path, original_file)
    with testhelpers.expect_exit_with_output(capsys, "No chapters were left after slide."):
        _run_slide_cmd([str(chaptered_audio_file_path), "-d", "50.0"])


def test_trim_and_slide_backwards(tmp_path, chaptered_audio_file_path):
    """Trim a length from the beginning of a file while shifting everything backwards."""
    cmd = [str(chaptered_audio_file_path), "--trim-start", "3.6", "-d", "-1"]
    expected = [
        SegmentData(id=0, title="110Hz - Soft",
                    start_time=00.0, file_start_time=00.0,
                    end_time=00.4, file_end_time=00.4),
        SegmentData(id=1, title="220Hz - Loud",
                    start_time=00.4, file_start_time=00.4,
                    end_time=02.9, file_end_time=02.9),
        SegmentData(id=2, title="220Hz - Soft",
                    start_time=02.9, file_start_time=02.9,
                    end_time=05.4, file_end_time=05.4),
        SegmentData(id=3, title="330Hz - Loud",
                    start_time=05.4, file_start_time=05.4,
                    end_time=07.9, file_end_time=07.9),
        SegmentData(id=4, title="330Hz - Soft",
                    start_time=07.9, file_start_time=07.9,
                    end_time=10.4, file_end_time=10.4),
        SegmentData(id=5, title="440Hz - Loud",
                    start_time=10.4, file_start_time=10.4,
                    end_time=12.9, file_end_time=12.9),
        SegmentData(id=6, title="440Hz - Soft",
                    start_time=12.9, file_start_time=12.9,
                    end_time=16.399, file_end_time=16.399),
    ]
    _slide_and_check_segments(cmd, chaptered_audio_file_path, expected)


def test_slide_overshoot_forward(tmp_path, chaptered_audio_file_path):
    """Slide some chapters over the forward edge."""
    cmd = [str(chaptered_audio_file_path), "-d", "12.5"]
    expected = [
        SegmentData(id=0, title="110Hz - Loud",
                    start_time=00.0, file_start_time=00.0,
                    end_time=15.0, file_end_time=15.0),
        SegmentData(id=1, title="110Hz - Soft",
                    start_time=15.0, file_start_time=15.0,
                    end_time=17.5, file_end_time=17.5),
        SegmentData(id=2, title="220Hz - Loud",
                    start_time=17.5, file_start_time=17.5,
                    end_time=19.999, file_end_time=19.999),
    ]
    _slide_and_check_segments(cmd, chaptered_audio_file_path, expected)


def test_slide_overshoot_backwards(tmp_path, chaptered_audio_file_path):
    """Slide some chapters over the rear edge."""
    cmd = [str(chaptered_audio_file_path), "-d", "-12.5"]
    expected = [
        SegmentData(id=0, title="330Hz - Soft",
                    start_time=00.0, file_start_time=00.0,
                    end_time=02.5, file_end_time=02.5),
        SegmentData(id=1, title="440Hz - Loud",
                    start_time=02.5, file_start_time=02.5,
                    end_time=05.0, file_end_time=05.0),
        SegmentData(id=2, title="440Hz - Soft",
                    start_time=05.0, file_start_time=05.0,
                    end_time=19.999, file_end_time=19.999),
    ]
    _slide_and_check_segments(cmd, chaptered_audio_file_path, expected)
