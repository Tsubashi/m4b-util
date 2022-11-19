"""Test Split-by-silence."""
from pathlib import Path

import pytest

from m4b_util.split import SegmentData, SilenceFinder


fake_input = Path("Not-a-real-file")


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
    sf = SilenceFinder(fake_input)
    sf._ffoutput = lines
    assert sf._get_segment_times() == expected


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
    sf = SilenceFinder(fake_input, start_time=1.25)
    sf._ffoutput = lines
    assert sf._get_segment_times() == expected


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
        "[silencedetect @ 0x12860aa70] silence_start: 22.5000",
    ]
    expected = [(5.0, 7.5), (10.0, 12.5), (15.0, 17.5), (20.0, 22.5)]
    sf = SilenceFinder(fake_input, start_time=1.25)
    sf._ffoutput = lines
    assert sf._get_segment_times() == expected


def test_get_segment_times_empty():
    """Notice when we don't have any silence to extract."""
    expected = None
    sf = SilenceFinder(fake_input, start_time=1.25)
    sf._ffoutput = [""]
    assert sf._get_segment_times() == expected


def test_run_silencedetect(silences_file_path):
    """Get ffmpeg output from silencedetect filter."""
    expected = [
        "silence_start: 2.49979",
        "silence_end: 5.0001 | silence_duration: 2.50031",
        "silence_start: 7.49992",
        "silence_end: 10.0001 | silence_duration: 2.50017",
        "silence_start: 12.4999",
        "silence_end: 15.0001 | silence_duration: 2.50012",
        "silence_start: 17.5",
        "size=N/A time=00:00:20.01 bitrate=N/A",
    ]
    sf = SilenceFinder(
        input_path=silences_file_path,
        silence_duration=0.25
    )
    sf._run_silencedetect()
    for item in expected:
        match_list = [line for line in sf._ffoutput if item in line]
        assert len(match_list) == 1


def test_run_silencedetect_fail(tmp_path, capsys):
    """Get ffmpeg output from a failed silencedetect filter."""
    fake_file = tmp_path / "Not-a-real-file.mp3"
    open(fake_file, 'a').close()
    sf = SilenceFinder(fake_file)
    with pytest.raises(SystemExit) as e:
        sf._run_silencedetect()
    assert (e.value.code == 1)
    output = capsys.readouterr()
    assert "Could not determine segment times." in output.out


def test_run_silencedetect_no_silence(silences_file_path):
    """Get ffmpeg output from a no-silence-detected run."""
    unexpected = [
        "silence_start",
        "silence_end",
        "silence_duration",
    ]
    sf = SilenceFinder(silences_file_path)
    sf._run_silencedetect()
    for item in unexpected:
        match_list = [line for line in sf._ffoutput if item in line]
        assert len(match_list) == 0


def test_run_silencedetect_variable_start_end_times(silences_file_path):
    """Get ffmpeg output from silencedetect filter."""
    expected = [
        "silence_end: 5.0001 | silence_duration: 2.50031",
        "silence_start: 7.49992",
        "silence_end: 10.0001 | silence_duration: 2.50017",
        "silence_start: 12.4999",
        "silence_end: 15.0001 | silence_duration: 2.50012",
        "size=N/A time=00:00:13.00 bitrate=N/A",
    ]
    sf = SilenceFinder(
        input_path=silences_file_path,
        silence_duration=0.25,
        start_time=3,
        end_time=16
    )
    sf._run_silencedetect()
    for item in expected:
        match_list = [line for line in sf._ffoutput if item in line]
        assert len(match_list) == 1


def test_find(silences_file_path):
    """Find silences in a file."""
    expected = [
        SegmentData(id=0, start_time=00.0000, end_time=2.49979),
        SegmentData(id=1, start_time=05.0001, end_time=7.49992),
        SegmentData(id=2, start_time=10.0001, end_time=12.4999),
        SegmentData(id=3, start_time=15.0001, end_time=17.5000),
        SegmentData(id=4, start_time=20.0107, end_time=20.0100)
    ]
    actual = SilenceFinder(silences_file_path, silence_duration=0.25).find()
    assert actual == expected
