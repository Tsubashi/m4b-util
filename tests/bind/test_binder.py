"""Test the Binder class."""
from pathlib import Path
import shutil
from subprocess import run
from tempfile import TemporaryDirectory

from natsort import natsorted
import pytest

from m4b_util.bind.Binder import Binder
from m4b_util.helpers import ffprobe
import testhelpers


def _do_scan(binder, files, **kwargs):
    """Use binder to scan files, then test the binder's attributes based on kwargs."""
    binder.files = natsorted(files)
    binder._scan_files(binder.files)  # noqa
    for attr_name, attr_value in kwargs.items():
        assert (getattr(binder, attr_name) == attr_value)


def _add_metadata(file_path, **kwargs):
    """Add metadata specified by kwargs to file_path."""
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / f"temp{file_path.suffix}"
        cmd = ["ffmpeg", "-i", file_path]

        # Add in metadata from kwargs
        for key, value in kwargs.items():
            cmd.append("-metadata")
            cmd.append(f"{key}={value}")

        # Add output path
        cmd.append(tmp_path)

        run(cmd, capture_output=True, check=True)

        shutil.move(tmp_path, file_path)


def test_output_path():
    """Set the output path in various ways."""
    b = Binder()
    assert (str(b.output_path) == "None - None.m4b")  # Default
    # Author
    b.author = "Write-y McAuthor"
    assert (str(b.output_path) == "Write-y McAuthor - None.m4b")
    # Author + Title
    b.title = "Test Book: An exercise of m4b-util"
    assert (str(b.output_path) == "Write-y McAuthor - Test Book: An exercise of m4b-util.m4b")
    # Dir + Author + Title
    b.output_dir = "Fake Dir"
    assert (str(b.output_path) == "Fake Dir/Write-y McAuthor - Test Book: An exercise of m4b-util.m4b")
    # Dir + Name (Overwrites Author & Title), Adds m4b extension
    b.output_name = "Author McWrite-y"
    assert (str(b.output_path) == "Fake Dir/Author McWrite-y.m4b")
    # Dir + Name (Overwrites Author & Title), does not double up m4b extension
    b.output_name = "Author McWrite-y.m4b"
    assert (str(b.output_path) == "Fake Dir/Author McWrite-y.m4b")


def test_file_scanner_mp3(mp3_path, expected_data):
    """Get the correct data from a set of mp3 files."""
    _do_scan(
        Binder(),
        mp3_path.glob("*"),
        title=None,
        author=None,
        date=None,
        chapters=expected_data['mp3']['chapters'],
        metadata=expected_data['mp3']['metadata']
    )


def test_file_scanner_wav(wav_path, expected_data):
    """Get the correct data from a set of mp3 files."""
    _do_scan(
        Binder(),
        wav_path.glob("*"),
        title=None,
        author=None,
        date=None,
        chapters=expected_data['default']['chapters'],
        metadata=expected_data['default']['metadata']
    )


def test_file_scanner_m4a(m4a_path, expected_data):
    """Get the correct data from a set of mp3 files."""
    _do_scan(
        Binder(),
        m4a_path.glob("*"),
        title=None,
        author=None,
        date=None,
        chapters=expected_data['default']['chapters'],
        metadata=expected_data['default']['metadata']
    )


def test_file_scanner_use_filenames(mp3_path, expected_data):
    """Use filenames instead of metadata when scanning files."""
    b = Binder()
    b.use_filename = True
    _do_scan(
        b,
        mp3_path.glob("*"),
        title=None,
        author=None,
        date=None,
        chapters=expected_data['use_filename']['chapters'],
        metadata=expected_data['use_filename']['metadata']
    )


def test_metadata_from_input(mp3_path):
    """Pick up metadata from our input files."""
    file = mp3_path / "2 - 220Hz.mp3"
    _add_metadata(file, album="Book Title", artist="Author McWrite-y", date="2022")
    _do_scan(
        Binder(),
        mp3_path.glob("*"),
        title="Book Title",
        author="Author McWrite-y",
        date="2022"
    )


def test_grab_first_metadata_only(mp3_path):
    """Only fill metadata items the first time we see them."""
    file = mp3_path / "2 - 220Hz.mp3"
    _add_metadata(file, album="Book Title", artist="Author McWrite-y")
    second_file = mp3_path / "3 - 330Hz.mp3"
    _add_metadata(second_file, album="Fake Book Title", artist="Not a Real Author")
    _do_scan(
        Binder(),
        mp3_path.glob("*"),
        title="Book Title",
        author="Author McWrite-y"
    )


def test_prefer_user_supplied_metadata(mp3_path):
    """Don't fill metadata from files if we already have it."""
    file = mp3_path / "2 - 220Hz.mp3"
    _add_metadata(file, album="Fake Book Title", artist="Not Author McWrite-y", date="1011")
    b = Binder()
    b.title = "Book Title"
    b.author = "Author McWrite-y"
    b.date = "2022"
    _do_scan(
        b,
        mp3_path.glob("*"),
        title="Book Title",
        author="Author McWrite-y",
        date="2022"
    )


def test_scanning_nonaudio_file(mp3_path, capsys):
    """Print a warning if we can't parse a file."""
    # Create a blank mp3 file
    open(mp3_path / "not-really-audio.mp3", 'a').close()
    _do_scan(Binder(), mp3_path.glob("*"))
    output = capsys.readouterr()
    assert ("Warning: Unable to parse" in output.out)


def test_status_updates_during_scan(wav_path, capsys):
    """Show the user what we are doing while we scan."""
    _do_scan(Binder(), wav_path.glob("*"))
    output = capsys.readouterr()
    assert (output.out == "Collecting file data...\nFile scan complete.\n")


def test_concatenation(m4a_path):
    """Concatenate all the files into one."""
    b = Binder()
    b.temp_files = natsorted(m4a_path.glob("*"))
    out_file_path = b._concatenate_all_audio_files()

    probe = ffprobe.run_probe(out_file_path)
    assert probe
    assert probe.format['duration'] == "40.022000"
    assert probe.audio['duration'] == "40.021333"
    assert not probe.tags.get('title')


def test_filenames_with_single_quotes(m4a_path):
    """Create a well-formed file when one of the inputs has quotes in its name."""
    orig_file = m4a_path / "2 - 220Hz.m4a"
    quote_file = m4a_path / "2 - '220Hz'.m4a"
    shutil.move(orig_file, quote_file)

    b = Binder()
    b.temp_files = natsorted(m4a_path.glob("*"))
    out_file_path = b._concatenate_all_audio_files()

    probe = ffprobe.run_probe(out_file_path)
    assert probe
    assert probe.format['duration'] == "40.022000"
    assert probe.audio['duration'] == "40.021333"  # If the file is broken, this will be shorter
    assert not probe.tags.get('title')


def test_decode_durations(wav_path):
    """Read the duration of a file by decoding it."""
    file = wav_path / "4 - 440Hz.wav"
    b = Binder()
    meta_duration = b._get_duration(file)
    b.decode_durations = True
    decoded_duration = b._get_duration(file)
    assert (meta_duration == decoded_duration == 5000)


def test_decode_duration_fake_file(tmp_path):
    """Read the duration of a file by decoding it."""
    file = tmp_path / "not-really-audio.mp3"
    open(file, 'a').close()
    b = Binder()
    b.decode_durations = True
    with pytest.raises(RuntimeError) as e:
        b._get_duration(file)
    assert ("Could not get audio stream." in str(e.value))


def test_get_duration_no_metadata(tmp_path, capsys):
    """Throw an error if no duration metadata, such as in mkv's."""
    # Create the file
    file = tmp_path / "no_duration.mkv"
    cmd = ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=48000:duration=2.5",
           "-filter_complex", "[0]apad=pad_dur=2.5[s0]", "-map", "[s0]", file]
    run(cmd, capture_output=True, check=True)

    # Make sure it reads successfully if decode_durations is set
    b = Binder()
    b.decode_durations = True
    assert (b._get_duration(file) == 5000)

    # Make sure it doesn't work when decode_durations is not set
    b.decode_durations = False
    with pytest.raises(RuntimeError) as e:
        b._get_duration(file)
    assert ("Cannot parse duration listed in file." in str(e.value))

    # Make sure it gets handled and mentioned to user during scanning
    _do_scan(Binder(), [file])
    output = capsys.readouterr()
    assert ("Failed to determine duration" in output.out)


def test_add_chapter_info(m4a_path):
    """Add chapter info to a file."""
    file = m4a_path / "4 - 440Hz.m4a"
    b = Binder()
    b.chapters.append({"title": "Sound", "startTime": 0})
    b.chapters.append({"title": "Silence", "startTime": 2500})
    out_file_path = b._add_chapter_info(file)

    probe = ffprobe.run_probe(out_file_path)
    assert probe
    assert len(probe.chapters) == 2
    assert probe.chapters[0]['tags']['title'] == "Sound"
    assert probe.chapters[1]['tags']['title'] == "Silence"


def test_add_cover(m4a_path, test_data_path):
    """Add chapter info to a file."""
    file = m4a_path / "4 - 440Hz.m4a"
    b = Binder()
    b.cover = test_data_path / "cover.png"
    out_file_path = b._add_cover(file)

    probe = ffprobe.run_probe(out_file_path)
    assert probe
    assert probe.streams[1]['codec_name'] == "png"


def test_ffmpeg_fail():
    """Handle it when an ffmpeg run fails."""
    b = Binder()
    with pytest.raises(SystemExit) as e:
        b._run_ffmpeg(["ffmpeg", "-invalid_option"], "Make ffmpeg fail.")
    assert (e.value.code == 1)


def test_ffmpeg_fail_keep_temp_files():
    """Handle it when an ffmpeg run fails."""
    b = Binder()
    b.keep_temp_files = True
    canary = Path(b.temp_path) / "canary"
    open(canary, 'a').close()
    with pytest.raises(SystemExit) as e:
        b._run_ffmpeg(["ffmpeg", "-invalid_option"], "Make ffmpeg fail.")
    assert (e.value.code == 1)
    expected_files = ["canary"]
    testhelpers.check_output_folder(b.temp_path, expected_files, check_func=testhelpers.assert_file_path_is_file)


def test_bind_no_files(capsys):
    """Show an error when there are no files to bind."""
    b = Binder()
    assert (b.bind() is False)
    output = capsys.readouterr()
    assert ("No input files found" in output.out)


def test_bind_keep_temp_files(mp3_path, tmp_path, test_data_path, capsys):
    """Keep all temp files when asked."""
    out_file_path = tmp_path / "Book.m4b"
    b = Binder()
    b.files = natsorted(mp3_path.glob("*"))
    b.cover = test_data_path / "cover.png"
    b.keep_temp_fiyyles = True
    b.output_name = str(out_file_path)
    b.bind()

    # Make sure we told the user where the temp dir is
    output = capsys.readouterr()
    assert ("Temp files can be found at" in output.out)

    # Make sure the files we expect are there
    expected_files = (
        "1 - 110Hz.m4a",
        "2 - 220Hz.m4a",
        "3 - 330Hz.m4a",
        "4 - 440Hz.m4a",
        "5 - 550Hz.m4a",
        "6 - 660Hz.m4a",
        "7 - 770Hz.m4a",
        "8 - 880Hz.m4a",
        "long.m4a",
        "filelist",
        "coverless.m4b",
        "finished.m4b",
        "ffmetadata",
    )
    testhelpers.check_output_folder(b.temp_path, expected_files, check_func=testhelpers.assert_file_path_is_file)


def test_bind_coverless(mp3_path, tmp_path):
    """Create an audiobook without a cover."""
    out_file_path = tmp_path / "Book.m4b"
    b = Binder()
    b.files = natsorted(mp3_path.glob("*"))
    b.output_name = str(out_file_path)
    b.bind()

    # Verify output
    probe = ffprobe.run_probe(out_file_path)
    assert probe

    # Check chapters
    assert len(probe.chapters) == 8
    assert probe.chapters[0]['tags']['title'] == "1"
    assert probe.chapters[1]['tags']['title'] == "2"
    assert probe.chapters[2]['tags']['title'] == "3"
    assert probe.chapters[3]['tags']['title'] == "4"
    assert probe.chapters[4]['tags']['title'] == "5"
    assert probe.chapters[5]['tags']['title'] == "6"
    assert probe.chapters[6]['tags']['title'] == "7"
    assert probe.chapters[7]['tags']['title'] == "8"

    # Check duration
    assert probe.format['duration'] == "40.022000"
    assert probe.audio['duration'] == "40.021333"

    # Check metadata
    assert probe.tags['title'] == "None"
    assert probe.tags['artist'] == "None"
    assert probe.tags['album'] == "None"
    assert probe.tags['date'] == "None"
    assert probe.tags['genre'] == "Audiobook"


def test_bind_covered(mp3_path, tmp_path, test_data_path):
    """Create an audiobook with a cover."""
    b = Binder()
    b.files = natsorted(mp3_path.glob("*"))
    b.output_dir = str(tmp_path)
    b.output_name = "Book.m4b"
    b.cover = test_data_path / "cover.png"
    b.bind()

    # Verify output
    probe = ffprobe.run_probe(tmp_path / "Book.m4b")
    assert probe

    # Check chapters
    assert len(probe.chapters) == 8
    assert probe.chapters[0]['tags']['title'] == "1"
    assert probe.chapters[1]['tags']['title'] == "2"
    assert probe.chapters[2]['tags']['title'] == "3"
    assert probe.chapters[3]['tags']['title'] == "4"
    assert probe.chapters[4]['tags']['title'] == "5"
    assert probe.chapters[5]['tags']['title'] == "6"
    assert probe.chapters[6]['tags']['title'] == "7"
    assert probe.chapters[7]['tags']['title'] == "8"

    # Check duration
    assert probe.format['duration'] == "40.022000"
    assert probe.audio['duration'] == "40.021333"

    # Check metadata
    assert probe.tags['title'] == "None"
    assert probe.tags['artist'] == "None"
    assert probe.tags['album'] == "None"
    assert probe.tags['date'] == "None"

    # Check cover
    assert probe.streams[2]['codec_name'] == "png"
