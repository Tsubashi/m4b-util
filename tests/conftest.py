"""PyTest Configuration."""
from pathlib import Path
from subprocess import run

import pytest

from expected_data import expected_data  # noqa


def _generate_tone_files(dir_path, extension):
    """Generate a folder of sine wave audio files.

    Creates 8 files with 2.5 seconds of pure sine wave at the base frequency, increasing by the base frequency
    each time.

    :param dir_path: Base folder in which to place the output.
    :param extension: File extension (and thus, implicitly, the format) to use for the output files.
    """
    base_frequency = 110  # Hz
    for i in range(1, 9):
        frequency = base_frequency * i
        output_path = dir_path / f"{i} - {frequency}Hz.{extension}"
        cmd = ["ffmpeg", "-f", "lavfi", "-i", f"sine=frequency={frequency}:sample_rate=48000:duration=2.5",
               "-filter_complex", "[0]apad=pad_dur=2.5[s0]", "-map", "[s0]", output_path]
        run(cmd, capture_output=True, check=True)


@pytest.fixture(scope='session')
def test_data_path():
    """Path to the test data directory."""
    # Since __file__ returns the file name, we need to call parent to get the directory
    return Path(__file__).parent.joinpath("data").absolute()


@pytest.fixture()
def wav_path(tmp_path):
    """Path to a temporary folder with a number of short wav files."""
    wav_path = tmp_path / "wav"
    wav_path.mkdir()
    _generate_tone_files(wav_path, "wav")

    return wav_path


@pytest.fixture()
def mp3_path(tmp_path):
    """Path to a temporary folder with a number of short mp3 files."""
    mp3_path = tmp_path / "mp3"
    mp3_path.mkdir()
    _generate_tone_files(mp3_path, "mp3")

    return mp3_path


@pytest.fixture()
def m4a_path(tmp_path):
    """Path to a temporary folder with a number of short m4a files."""
    m4a_path = tmp_path / "m4a"
    m4a_path.mkdir()
    _generate_tone_files(m4a_path, "m4a")

    return m4a_path


@pytest.fixture()
def video_only_file(tmp_path):
    """File containing multiple segments of louder and softer sounds."""
    output_path = tmp_path / "video_only.mp4"
    cmd = ["ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=5.3:size=qcif:rate=10", output_path]
    run(cmd, capture_output=True, check=True)
    return output_path
