"""Test the Bind subcommand."""
from unittest.mock import patch

import testhelpers

from m4b_util.__main__ import allowed_commands, main as m4b_main


def _run_main_cmd(arg_list, expected_exit=0):
    argv_patch = ["m4b-util"]
    argv_patch.extend(arg_list)

    with patch("sys.argv", argv_patch):
        with testhelpers.expect_exit(expected_exit):
            m4b_main()


def test_print_version(capsys):
    """Show the order the files would be bound in, if asked."""
    _run_main_cmd(["version"])

    output = capsys.readouterr()
    expected_output = "m4b-util, Version"  # Don't specify the exact version, so we don't have to update it every tag.
    assert expected_output in output.out


def test_unrecognized_command(capsys):
    """Throw an error on an unrecognized sub-command."""
    _run_main_cmd(["definitely-not-a-real-command"], -1)

    output = capsys.readouterr()
    expected_output = "Unrecognized command"
    assert expected_output in output.out


def test_all_commands_help(capsys):
    """Display help menu from all commands."""
    for command in allowed_commands:
        _run_main_cmd([command, "--help"])
