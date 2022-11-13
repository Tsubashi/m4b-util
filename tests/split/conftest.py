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
