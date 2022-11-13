"""The Splitter Class."""
from m4b_util.helpers import ffprogress


class Splitter:
    """Holds all the info and methods for splitting a file."""

    def __init__(self):
        """Set default values."""
        self.segment_list = list()
        self.input_file = None
        self.start_time = 0
        self.end_time = 0
        self.ffoutput = ""

    def split(self):
        """Do the actual splitting."""
        # Remove any segments less than 1 second
        # Use .copy() so that we can modify the original without throwing off the iterator
        for start, end in output.copy():
            if end - start < 1.0:
                output.remove((start, end))

    def _extract_cover(self, output_path):
        """Dump an audio file's cover image to disk."""
        allowed_extensions = [".png", ".jpg", ".jpeg"]
        if output_path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"Output extension must be one of {allowed_extensions}")
        cmd = ["ffmpeg", "-y", "-i", self.input_path, output_path]
        ffprogress.run(cmd, "Extracting cover")


