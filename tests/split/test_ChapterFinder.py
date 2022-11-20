from m4b_util.split import ChapterFinder, SegmentData


def test_find_chapters(chaptered_audio_file_path):
    """Read the chapter metadata into an object."""
    expected = [
        SegmentData(id=0, start_time=00.0, end_time=02.5, title="110Hz - Loud"),
        SegmentData(id=1, start_time=02.5, end_time=05.0, title="110Hz - Soft"),
        SegmentData(id=2, start_time=05.0, end_time=07.5, title="220Hz - Loud"),
        SegmentData(id=3, start_time=07.5, end_time=10.0, title="220Hz - Soft"),
        SegmentData(id=4, start_time=10.0, end_time=12.5, title="330Hz - Loud"),
        SegmentData(id=5, start_time=12.5, end_time=15.0, title="330Hz - Soft"),
        SegmentData(id=6, start_time=15.0, end_time=17.5, title="440Hz - Loud"),
        SegmentData(id=7, start_time=17.5, end_time=19.999, title="440Hz - Soft"),
    ]
    assert ChapterFinder(chaptered_audio_file_path).find() == expected


def test_start_end_times(chaptered_audio_file_path):
    """Filter out chapters based on a custom start and end time."""
    expected = [
        SegmentData(id=2, start_time=05.0, end_time=07.5, title="220Hz - Loud"),
        SegmentData(id=3, start_time=07.5, end_time=10.0, title="220Hz - Soft"),
        SegmentData(id=4, start_time=10.0, end_time=12.5, title="330Hz - Loud"),
    ]
    assert ChapterFinder(
        chaptered_audio_file_path,
        start_time=2.75,
        end_time=14.0
    ).find() == expected


def test_find_chapters_no_chapters(mp3_path):
    """Read an audio file that has no chapter data."""
    assert ChapterFinder(mp3_path / "1 - 110Hz.mp3").find() == []


def test_find_chapters_unreadable_file(tmp_path):
    """Find no chapters in a non-audio file."""
    fakefile = tmp_path / "Not-a-real-file.mp3"
    open(fakefile, 'a').close()
    assert ChapterFinder(fakefile).find() == []
