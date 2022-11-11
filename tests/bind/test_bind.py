"""Test the Bind subcommand."""
from unittest.mock import patch

import m4b_util


def _run_bind_cmd(arg_list):
    argv_patch = ["m4b-util", "bind"]
    argv_patch.extend(arg_list)

    with patch("sys.argv", argv_patch):
        m4b_util.bind()


def test_show_order(mp3_path, capsys):
    """Show the order the files would be bound in, if asked."""
    _run_bind_cmd([str(mp3_path), "--show-order"])

    output = capsys.readouterr()
    expected_output = ('  0:    1 - 110Hz.mp3\n'
                       '  1:    2 - 220Hz.mp3\n'
                       '  2:    3 - 330Hz.mp3\n'
                       '  3:    4 - 440Hz.mp3\n'
                       '  4:    5 - 550Hz.mp3\n'
                       '  5:    6 - 660Hz.mp3\n'
                       '  6:    7 - 770Hz.mp3\n'
                       '  7:    8 - 880Hz.mp3\n'
                       )
    assert (output.out == expected_output)


def test_nonexistent_output_dir(capsys):
    """Alert the user if the output dir doesn't exist."""
    _run_bind_cmd(["fake/input/dir", "--output-dir", "/some/nonexistent/directory/"])

    output = capsys.readouterr()
    assert ("is not a directory" in output.out)


def test_bind_wav_defaults(wav_path, tmp_path, capsys):
    """Bind a folder of wav files into and audiobook."""
    _run_bind_cmd([str(wav_path), "-e", "wav", "-o", str(tmp_path)])

    # Check for output
    output_path = tmp_path / "None - None.m4b"
    assert output_path.is_file()

    probe = m4b_util.helpers.ffprobe.run_probe(output_path)
    assert probe
    assert probe.format['duration'] == "40.022000"
    assert probe.audio['duration'] == "40.021333"
    assert probe.tags['title'] == "None"
    assert probe.tags['artist'] == "None"
    assert probe.tags['album'] == "None"
    assert probe.tags['date'] == "None"
    assert probe.tags['genre'] == "Audiobook"

    # Make sure we tell the user where the output file is. Since rich auto-wraps the output unpredictably, we will
    # just check to make sure the start of the message, and the book file name are present.
    output = capsys.readouterr()
    assert ("Writing " in output.out)
    assert ("None - None.m4b" in output.out)
