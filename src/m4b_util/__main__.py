"""Main Script for m4b-util."""
import argparse
import sys

from rich import print

from . import bind, split
from .__version__ import version


def _print_version():
    """Print the current version, then exit."""
    print(f"[green]m4b-util[/], Version '{version}'")
    return 0


# Set up the dictionary of commands. The values are tuples, first the function to run, second the description.
allowed_commands = {
    "bind": (bind, "Convert a folder of audio files into an m4b."),
    "split-by-silence": (split, "Split a file into smaller files by silence."),
    "version": (_print_version, "Print the program's version.")
}


def main():
    """Run the application."""
    # Write our usage message
    usage = ("m4b-util <command> [<args>]\n\n"
             "Allowed Commands:\n"
             )
    for name, (_, description) in allowed_commands.items():
        usage += f"{name:18}: {description}\n"
    usage += ("\nFor more help with a command, use m4b-util <command> --help\n"
              " \n"
              )

    # Set up argparse
    parser = argparse.ArgumentParser(
        prog="m4b-util",
        description='A Collection of utilities for interacting with m4b files.',
        usage=usage
    )
    parser.add_argument('command', help='Subcommand to run')
    # parse_args defaults to [1:] for args, but we need to exclude the rest of the args so they can be picked up by
    args = parser.parse_args(sys.argv[1:2])

    # Make sure args.command is always lowercase
    args.command = args.command.lower()

    if args.command not in allowed_commands:
        print("[bold red]Error:[/] Unrecognized command")
        print(parser.print_help())
        exit(-1)

    # Invoke the subcommand
    retcode = allowed_commands[args.command][0]()

    print("[green]Done![/]")
    exit(retcode)


# We don't test coverage for this, since we don't test it directly.
# We just make it simple enough that we can trust it works.
if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
