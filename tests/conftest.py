"""PyTest Configuration."""
from pathlib import Path
from subprocess import run

import pytest

from expected_data import expected_data  # noqa

# Let pytest know we would like them to handle asserts in our helper code
pytest.register_assert_rewrite("testhelpers")


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
def mp3_file_path(tmp_path):
    """A single mp3 file. 2.5s tone, 2.5s silence."""
    output_path = tmp_path / "single_file.mp3"
    cmd = ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5",
           "-filter_complex", "[0]apad=pad_dur=2.5[s0]", "-map", "[s0]", output_path]
    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def m4a_path(tmp_path):
    """Path to a temporary folder with a number of short m4a files."""
    m4a_path = tmp_path / "m4a"
    m4a_path.mkdir()
    _generate_tone_files(m4a_path, "m4a")

    return m4a_path


@pytest.fixture()
def m4a_file_path(tmp_path):
    """A single m4a file. 2.5s tone, 2.5s silence."""
    output_path = tmp_path / "single_file.m4a"
    cmd = ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5",
           "-filter_complex", "[0]apad=pad_dur=2.5[s0]", "-map", "[s0]", output_path]
    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def covered_audio_file(tmp_path, test_data_path):
    """Path to an m4a file with a cover image."""
    output_path = tmp_path / "covered_audio_file.m4a"
    cover_path = test_data_path / "cover.png"
    cmd = ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5",
           "-i", cover_path, "-c:v", "png",
           "-map", "0:a", "-map", "1", "-disposition:v:0", "attached_pic",
           output_path
           ]
    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def video_only_file(tmp_path):
    """File containing a single video stream test pattern."""
    output_path = tmp_path / "video_only.mp4"
    cmd = ["ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=5.3:size=qcif:rate=10", output_path]
    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def chaptered_audio_file_path(tmp_path):
    """File containing multiple chapters."""
    metadata = (
        ";FFMETADATA1\nmajor_brand=M4A\nminor_version=512\ncompatible_brands=M4A isomiso2\n"
        "title=Chaptered Audio\nartist=m4b-util\nalbum=Chaptered Audio\ndate=2022\ngenre=Audiobook\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=2499\ntitle=110Hz - Loud\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=2500\nEND=4999\ntitle=110Hz - Soft\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=5000\nEND=7499\ntitle=220Hz - Loud\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=7500\nEND=9999\ntitle=220Hz - Soft\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=10000\nEND=12499\ntitle=330Hz - Loud\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=12500\nEND=14999\ntitle=330Hz - Soft\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=15000\nEND=17499\ntitle=440Hz - Loud\n"
        "[CHAPTER]\nTIMEBASE=1/1000\nSTART=17500\nEND=19999\ntitle=440Hz - Soft\n"
    )
    metadata_file = tmp_path / "ffmetadata"
    with open(metadata_file, 'w') as f:
        print(metadata, file=f)
    output_path = tmp_path / "chaptered_audio.m4b"
    cmd = ["ffmpeg",
           "-i", metadata_file,
           "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5,volume=.5",
           "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=2.5,volume=.5",
           "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=2.5,volume=.5",
           "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5,volume=.5",
           "-filter_complex",
           "[1][2][3][4][5][6][7][8]concat=n=8:v=0:a=1[s0]",
           "-map", "[s0]", "-map_metadata", "0", "-map_chapters", "0",
           output_path
           ]
    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def silences_file_path(tmp_path):
    """File containing multiple segments of silence."""
    output_path = tmp_path / "file_with_silences.m4a"
    cmd = ["ffmpeg",
           "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5",
           "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=2.5",
           "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=2.5",
           "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5",
           "-filter_complex",
           "[0]apad=pad_dur=2.5[s0],[1]apad=pad_dur=2.5[s1],[2]apad=pad_dur=2.5[s2],[3]apad=pad_dur=2.5[s3],"
           "[s0][s1][s2][s3]concat=n=4:v=0:a=1[s4]", "-map", "[s4]",
           output_path
           ]

    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def abrupt_ending_file_path(tmp_path):
    """File containing multiple segments of silence, ending in non-silence."""
    output_path = tmp_path / "file_with_abrupt_end.m4a"
    cmd = ["ffmpeg",
           "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5",
           "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=2.5",
           "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=2.5",
           "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5",
           "-filter_complex",
           "[0]apad=pad_dur=2.5[s0],[1]apad=pad_dur=2.5[s1],[2]apad=pad_dur=2.5[s2],"
           "[s0][s1][s2][3]concat=n=4:v=0:a=1[s4]", "-map", "[s4]",
           output_path
           ]

    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def variable_volume_segments_file_path(tmp_path):
    """File containing multiple segments of louder and softer sounds."""
    output_path = tmp_path / "variable_volume_segments.m4b"
    cmd = ["ffmpeg",
           "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5,volume=.5",
           "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=2.5,volume=.5",
           "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=2.5,volume=.5",
           "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5,volume=1.5",
           "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2.5,volume=.5",
           "-filter_complex",
           "[0][1][2][3][4][5][6][7]concat=n=8:v=0:a=1[s0]", "-map", "[s0]",
           output_path
           ]
    run(cmd, capture_output=True, check=True)
    return output_path


@pytest.fixture()
def mkv_file_path(tmp_path):
    """An mkv file, for testing files without duration metadata."""
    # Create the file
    file = tmp_path / "no_duration.mkv"
    cmd = ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5",
           "-filter_complex", "[0]apad=pad_dur=2.5[s0]", "-map", "[s0]", file]
    run(cmd, capture_output=True, check=True)

    return file


@pytest.fixture()
def fake_file(tmp_path):
    """A file with no content."""
    file = tmp_path / "fake.file"
    open(file, 'a').close()
    return file
