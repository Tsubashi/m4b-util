"""Test the ffmpeg trim helpers."""
import pytest

from m4b_util.helpers.ffmpeg_trim import trim_args


def test_no_trim():
    """Leave the command alone when the whole file is wanted."""
    assert trim_args() == ([], [])
    assert trim_args(0.0, None) == ([], [])


def test_duration_only():
    """Cut from the start of the file without seeking."""
    assert trim_args(0.0, 2.5) == ([], ["atrim=duration=2.500000", "asetpts=PTS-STARTPTS"])


def test_start_within_preroll():
    """Trim from the start of the file when the range starts too early to seek ahead of it."""
    assert trim_args(0.4, 2.5) == ([], ["atrim=start=0.400000:duration=2.500000", "asetpts=PTS-STARTPTS"])


def test_start_and_duration():
    """Seek to just before the range, then trim the rest of the way."""
    assert trim_args(7.3, 2.5) == (
        ["-ss", "6.300000"],
        ["atrim=start=1.000000:duration=2.500000", "asetpts=PTS-STARTPTS"],
    )


def test_start_only():
    """Keep everything after the start time."""
    assert trim_args(7.5) == (["-ss", "6.500000"], ["atrim=start=1.000000", "asetpts=PTS-STARTPTS"])


def test_tiny_times_avoid_exponents():
    """Write very small times in fixed notation, since ffmpeg cannot read exponents."""
    assert trim_args(1.00001, 0.00005) == (
        ["-ss", "0.000010"],
        ["atrim=start=1.000000:duration=0.000050", "asetpts=PTS-STARTPTS"],
    )


def test_empty_duration():
    """Refuse to trim to nothing, since ffmpeg would keep the rest of the file instead."""
    with pytest.raises(ValueError):
        trim_args(0.0, 0.0)
    with pytest.raises(ValueError):
        trim_args(5.0, -1.0)
