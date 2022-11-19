"""ffprogress tests."""
import io
from unittest import mock

import pytest

from m4b_util.helpers import ffprobe, ffprogress


def test_to_ms():
    """Convert hr:min:sec.ms to milliseconds."""
    assert ffprogress.to_ms() == 0
    assert ffprogress.to_ms(sec=5, ms=555) == 5555
    assert ffprogress.to_ms(hour=5, min=5, sec=5, ms=555) == 18305555


@mock.patch("subprocess.Popen")
def test_ffprogress_class(popen):
    """Use the FFProgress class."""
    # Make sure output is initialized to None
    ff = ffprogress.FFProgress(["mocked_cmd"])
    assert ff.output is None

    # Set up Mock
    type(popen()).stdout = mock.PropertyMock(side_effect=[
        None,
        io.BytesIO(b"Duration: 01:00:00.00"),
        None,
        io.BytesIO(b""),
        io.BytesIO(b"out_time=00:00:00.00"),
        io.BytesIO(b"out_time=00:15:00.00"),
        io.BytesIO(b"out_time=00:30:00.00"),
        io.BytesIO(b"out_time=00:45:00.00"),
        io.BytesIO(b"out_time=01:00:00.00"),
        io.BytesIO(b"")
    ])
    popen().returncode = 0
    popen().poll.side_effect = [None, 0]

    expected = [0, 0, 25, 50, 75, 100, 100]
    for percent in ff.run():
        assert percent == expected.pop(0)


@mock.patch("subprocess.Popen")
def test_ffprogress_class_fail(popen):
    """Handle a command that fails."""
    ff = ffprogress.FFProgress(["mocked_cmd"])

    # Set up Mock
    popen().stdout = io.BytesIO(b"")
    popen().returncode = -1
    popen().poll.return_value = 0

    with pytest.raises(RuntimeError) as e:
        for percent in ff.run():
            assert percent == 0
    assert ("Error running command ['mocked_cmd']:" in str(e.value))


def test_run(tmp_path, capsys):
    """Use the helper run function."""
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
    ffprogress.run(cmd, "Testing progress message")
    output = capsys.readouterr()
    assert ("Testing progress message" in output.out)

    # Check that the output matches what we expect
    probe = ffprobe.run_probe(output_path)
    assert probe.audio
    assert probe.format['duration'] == "20.000000"


def test_run_fail(capsys):
    """Handle a crashing command when using the helper run function."""
    cmd = ["ffmpeg", "-not-a-real-option"]
    ffprogress.run(cmd, "Testing progress message")
    output = capsys.readouterr()
    assert ("Something went wrong with ffmpeg" in output.out)


def test_run_no_printing_errors():
    """Handle a crashing command with print_errors turned off."""
    cmd = ["ffmpeg", "-not-a-real-option"]
    with pytest.raises(RuntimeError) as e:
        ffprogress.run(cmd, print_errors=False)
    assert "Error running command" in str(e.value)
