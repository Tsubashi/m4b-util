m4b-util
---------
A command line utility for creating, editing, and generally working with m4b files.

## Sub-commands
This application is split into a number of subcommands which can be run from the main command. For a list of available 
commands, run `m4b-util --help`. For details on a specific sub-command, run `m4b-util <command> --help`.

### Bind
The `bind` sub-command is designed to take a folder of audio files and convert them to a single m4b, treating each 
individual file as its own chapter. It can get chapter names from the original files' metadata, original files' names,
from command line arguments, or just number them sequentially. By default, it only scans for mp3 files, but any file 
extension can be added via arguments.

**Example:**
```shell
$ m4b-util bind /path/to/inputs  --title "My Book" --cover /path/to/cover.png -e m4a -e .mp4 --output-dir /path/to/output 
```

### Split By Silence
The `split-by-silence` command takes a single audio file input, scans for silence, and writes out individual files 
containing the audio between the silences.

**Example:**
```shell
$ m4b-util split-by-silence /path/to/input.mp3 --output-dir /path/to/output --output_pattern "chapter_{:03d}.mp3"
```

### Split By Chapter
The `split-by-chapter` command takes a single audio file input with chapter metadata, scans through those chapters, 
and writes out individual files for each of those chapters.

**Example:**
```shell
$ m4b-util split-by-chapter /path/to/input.mp3 --output-dir /path/to/output --output_pattern "chapter_{:03d}.mp3"
```