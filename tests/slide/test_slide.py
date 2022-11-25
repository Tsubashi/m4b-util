"""Slide command tests."""
import shutil
from unittest import mock

from m4b_util import slide
from m4b_util.helpers import ChapterFinder, SegmentData


def _run_slide_cmd(arg_list):
    """Patch the runtime arguments, then run the split command."""
    argv_patch = ["m4b-util", "slide"]
    argv_patch.extend(arg_list)

    with mock.patch("sys.argv", argv_patch):
        slide.run()


def test_slide(tmp_path, chaptered_audio_file_path):
    """Slide all chapters."""
    original_file = tmp_path / "original.m4b"
    shutil.copy(chaptered_audio_file_path, original_file)
    _run_slide_cmd([chaptered_audio_file_path, "-d", "1.0"])
    segment_list = ChapterFinder(chaptered_audio_file_path).find()
    expected = [
        SegmentData(id=0, start_time=01.0, end_time=03.5, title="110Hz - Loud"),
        SegmentData(id=1, start_time=03.5, end_time=06.0, title="110Hz - Soft"),
        SegmentData(id=2, start_time=06.0, end_time=08.5, title="220Hz - Loud"),
        SegmentData(id=3, start_time=08.5, end_time=11.0, title="220Hz - Soft"),
        SegmentData(id=4, start_time=11.0, end_time=13.5, title="330Hz - Loud"),
        SegmentData(id=5, start_time=13.5, end_time=16.0, title="330Hz - Soft"),
        SegmentData(id=6, start_time=16.0, end_time=18.5, title="440Hz - Loud"),
        SegmentData(id=7, start_time=18.5, end_time=19.999, title="440Hz - Soft"),
    ]
    assert segment_list == expected


def test_slide_segment_list():
    """Shift all entries in a segment list, except for the final end time."""
    input = [
        SegmentData(id=0, start_time=00.0, end_time=05.0),
        SegmentData(id=1, start_time=05.0, end_time=10.0),
        SegmentData(id=2, start_time=10.0, end_time=15.0),
        SegmentData(id=3, start_time=15.0, end_time=20.0),
    ]
    expected = [
        SegmentData(id=0, start_time=00.5, end_time=05.5),
        SegmentData(id=1, start_time=05.5, end_time=10.5),
        SegmentData(id=2, start_time=10.5, end_time=15.5),
        SegmentData(id=3, start_time=15.5, end_time=20.0),
    ]
    output = Slider()._slide_segment_list(input, 0.5)
    assert output == expected
