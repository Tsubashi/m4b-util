from subprocess import run

import pytest


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
