import pytest

from m4b_util.helpers import cover_utils, ffprobe


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


def test_add_cover(tmp_path, test_data_path, m4a_file_path):
    """Add a cover image to a file."""
    out_file_path = tmp_path / "covered.m4a"
    cover_utils.add_cover(m4a_file_path, test_data_path / "cover.png", out_file_path)

    probe = ffprobe.run_probe(out_file_path)
    assert probe
    assert probe.streams[1]['codec_name'] == "png"


def test_add_cover_invalid_file(tmp_path, m4a_file_path):
    """Throw an error if the file cannot have a cover image."""
    out_file_path = tmp_path / "covered.m4a"
    fake_cover = tmp_path / "fake.png"
    open(fake_cover, 'a').close()
    with pytest.raises(RuntimeError) as e:
        cover_utils.add_cover(m4a_file_path, fake_cover, out_file_path)
    assert "Invalid data found when processing input" in str(e.value)
