import pytest

from m4b_util.helpers import cover_utils


def test_extract_cover(tmp_path, covered_audio_file):
    """Grab a cover."""
    output_extensions = ["png", "jpg", "jpeg", "JPG"]
    for extension in output_extensions:
        output = tmp_path / f"cover.{extension}"
        cover_utils.extract_cover(covered_audio_file, output)
        assert output.is_file()


def test_extract_cover_invalid_output_extension(tmp_path, covered_audio_file):
    """Reject invalid output extensions."""
    output = tmp_path / "cover.bad_ext"
    with pytest.raises(ValueError) as e:
        cover_utils.extract_cover(covered_audio_file, output)
    assert "Output extension must be one of" in str(e)


def test_extract_cover_non_covered_file(tmp_path, mp3_file_path, capsys):
    """Handle files without a cover image."""
    output = tmp_path / "cover.png"
    cover_utils.extract_cover(mp3_file_path, output)
    sysout = capsys.readouterr()
    assert "Unable to extract cover" in sysout.out
    assert "ffmpeg" not in sysout.out
    assert not output.exists()
