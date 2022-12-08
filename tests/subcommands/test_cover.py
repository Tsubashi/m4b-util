"""Cover Subcommand Tests."""
import filecmp
import shutil
from unittest import mock

import testhelpers

from m4b_util.helpers import ffprobe
from m4b_util.subcommands import cover


def _run_cover_cmd(arg_list):
    """Patch the runtime arguments, then run the split command."""
    argv_patch = ["m4b-util", "cover"]
    argv_patch.extend(arg_list)

    with mock.patch("sys.argv", argv_patch):
        cover.run()


def test_extract(tmp_path, test_data_path, covered_audio_file):
    """Extract a cover."""
    cover_path = tmp_path / "out.png"
    _run_cover_cmd([str(covered_audio_file), "-e", str(cover_path)])
    assert cover_path.is_file()
    assert filecmp.cmp(test_data_path / "cover.png", cover_path, shallow=False)


def test_apply(test_data_path, m4a_file_path):
    """Add a new cover."""
    cover_path = test_data_path / "cover.png"
    _run_cover_cmd([str(m4a_file_path), "-a", str(cover_path)])
    probe = ffprobe.run_probe(m4a_file_path)
    assert probe
    cover_streams = [stream for stream in probe.data.get('streams', list()) if stream.get('codec_name') == 'png']
    assert len(cover_streams) == 1
    assert cover_streams[0].get('disposition', {}).get("attached_pic") == 1


def test_overwrite(tmp_path, test_data_path, covered_audio_file):
    """Overwrite an exist cover."""
    new_cover_path = test_data_path / "cover2.png"
    original_file = tmp_path / "original.m4a"
    shutil.copy(covered_audio_file, original_file)
    _run_cover_cmd([str(covered_audio_file), "-a", str(new_cover_path)])
    probe = ffprobe.run_probe(covered_audio_file)
    assert probe
    cover_streams = [stream for stream in probe.data.get('streams', list()) if stream.get('codec_name') == 'png']
    assert len(cover_streams) == 1
    assert cover_streams[0].get('disposition', {}).get("attached_pic") == 1
    assert not filecmp.cmp(original_file, covered_audio_file, shallow=False)


def test_no_task_given(capsys):
    """Alert the user if no tasks are specified."""
    with testhelpers.expect_exit_with_output(
            capsys,
            expected_code=2,
            expected_text="At least one task must be specified"
    ):
        _run_cover_cmd(["Not-a-real.file"])
