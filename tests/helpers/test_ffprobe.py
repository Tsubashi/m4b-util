"""ffprobe tests."""
from m4b_util.helpers import ffprobe


def test_video_only(video_only_file):
    """Read in a video-only file."""
    probe = ffprobe.run_probe(video_only_file)
    assert probe.audio is None
    expected_tags = {
        'compatible_brands': 'isomiso2avc1mp41',
        'major_brand': 'isom',
        'minor_version': '512'
    }
    del probe.tags['encoder']  # Encoder will be different depending on the version of ffmpeg
    assert probe.tags == expected_tags


def test_probe_data(mp3_path):
    """Read an mp3 file."""
    file = mp3_path / "6 - 660Hz.mp3"
    probe = ffprobe.run_probe(file)
    assert probe

    expected = {
        'chapters': [],
        'format': {
            'bit_rate': '64376',
            'duration': '5.040000',
            'format_long_name': 'MP2/3 (MPEG audio layer 2/3)',
            'format_name': 'mp3',
            'nb_programs': 0,
            'nb_streams': 1,
            'probe_score': 51,
            'size': '40557',
            'start_time': '0.023021',
            'tags': {}
        },
        'streams': [{
            'avg_frame_rate': '0/0',
            'bit_rate': '64000',
            'bits_per_sample': 0,
            'channel_layout': 'mono',
            'channels': 1,
            'codec_long_name': 'MP3 (MPEG audio layer 3)',
            'codec_name': 'mp3',
            'codec_tag': '0x0000',
            'codec_tag_string': '[0][0][0][0]',
            'codec_type': 'audio',
            'disposition': {
                'attached_pic': 0,
                'captions': 0,
                'clean_effects': 0,
                'comment': 0,
                'default': 0,
                'dependent': 0,
                'descriptions': 0,
                'dub': 0,
                'forced': 0,
                'hearing_impaired': 0,
                'karaoke': 0,
                'lyrics': 0,
                'metadata': 0,
                'original': 0,
                'still_image': 0,
                'timed_thumbnails': 0,
                'visual_impaired': 0
            },
            'duration': '5.040000',
            'duration_ts': 71124480,
            'index': 0,
            'r_frame_rate': '0/0',
            'sample_fmt': 'fltp',
            'sample_rate': '48000',
            'start_pts': 324870,
            'start_time': '0.023021',
            'time_base': '1/14112000'
        }]
    }
    # Remove items that can change between tests
    del probe.data['format']['filename']
    del probe.data['format']['tags']['encoder']
    assert (probe.data == expected)


def test_probe_blank_file(tmp_path):
    """Return None when run on an un-parsable file."""
    file = tmp_path / "not-really-audio.mp3"
    open(file, 'a').close()
    probe = ffprobe.run_probe(file)
    assert not probe
