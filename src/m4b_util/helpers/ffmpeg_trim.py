"""Helpers for cutting a precise time range out of an audio file with ffmpeg."""

# How far before the requested start we ask ffmpeg to seek, in seconds.
# Input seeking is fast, but some ffmpeg versions drop a few milliseconds of audio right after the seek point.
# Seeking early and letting the atrim filter make the actual cut keeps the result sample-accurate.
SEEK_PREROLL = 1.0


def trim_args(start_time=None, duration=None):
    """Build the ffmpeg arguments needed to cut a time range out of an input file.

    Args:
        start_time (float): Where the range starts in the input, in seconds. None or 0 means the start of the file.
        duration (float): Length of the range, in seconds. None means to continue until the end of the file.

    Returns:
        tuple[list[str], list[str]]: Arguments to place before the `-i` of the input, and audio filters to apply
        to it. Both are empty when no trimming is needed.

    Raises:
        ValueError: If `duration` is zero or negative, as ffmpeg would treat that as "no limit" or reject it.
    """
    if duration is not None and duration <= 0.0:
        raise ValueError(f"Cannot trim to a duration of {duration} seconds.")

    start_time = start_time or 0.0
    # Only seek when there is at least a whole pre-roll to skip. Shorter ranges are trimmed from the file's start.
    seek_time = start_time - SEEK_PREROLL if start_time > SEEK_PREROLL else 0.0
    trim_start = start_time - seek_time

    # Times are written in fixed notation, as ffmpeg does not accept exponents such as "1e-05".
    seek_args = ["-ss", f"{seek_time:.6f}"] if seek_time > 0.0 else []

    trim_options = []
    if trim_start > 0.0:
        trim_options.append(f"start={trim_start:.6f}")
    if duration is not None:
        trim_options.append(f"duration={duration:.6f}")

    filters = []
    if trim_options:
        # Reset the timestamps after trimming, so the output starts at zero.
        filters = ["atrim=" + ":".join(trim_options), "asetpts=PTS-STARTPTS"]

    return seek_args, filters
