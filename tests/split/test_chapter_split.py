import pytest

from m4b_util.split_by_chapter import chapter_split
from m4b_util.split import SegmentData


def test_extract_cover(tmp_path, covered_audio_file):
    """Grab a cover."""
    output_extensions = ["png", "jpg", "jpeg", "JPG"]
    for extension in output_extensions:
        output = tmp_path / f"cover.{extension}"
        chapter_split._extract_cover(covered_audio_file, output)
        assert output.is_file()


def test_extract_cover_invalid_output_extension(tmp_path, covered_audio_file):
    """Reject invalid output extensions."""
    output = tmp_path / "cover.bad_ext"
    with pytest.raises(ValueError) as e:
        chapter_split._extract_cover(covered_audio_file, output)
    assert "Output extension must be one of" in str(e)


def test_find_chapters(chaptered_audio_file_path):
    """Read the chapter metadata into an object."""
    expected = [
        SegmentData(id=0, start_time=00.0, end_time=02.5, title="110Hz - Loud"),
        SegmentData(id=1, start_time=02.5, end_time=05.0, title="110Hz - Soft"),
        SegmentData(id=2, start_time=05.0, end_time=07.5, title="220Hz - Loud"),
        SegmentData(id=3, start_time=07.5, end_time=10.0, title="220Hz - Soft"),
        SegmentData(id=4, start_time=10.0, end_time=12.5, title="330Hz - Loud"),
        SegmentData(id=5, start_time=12.5, end_time=15.0, title="330Hz - Soft"),
        SegmentData(id=6, start_time=15.0, end_time=17.5, title="440Hz - Loud"),
        SegmentData(id=7, start_time=17.5, end_time=19.999, title="440Hz - Soft"),
    ]
    assert chapter_split._read_chapter_metadata(chaptered_audio_file_path) == expected


def test_run_splits(chaptered_audio_file_path):
