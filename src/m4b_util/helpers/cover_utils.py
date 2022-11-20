"""Utility functions relating to cover images."""
from rich import print

from m4b_util.helpers import ffprogress


def extract_cover(input_path, output_path):
    """Dump an audio file's cover image to disk.

    :param input_path: The file to extract the cover from
    :param output_path: Where to put the cover, including name. Must end in .png, .jpg, or ,jpeg
    """
    allowed_extensions = [".png", ".jpg", ".jpeg"]
    if output_path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Output extension must be one of {allowed_extensions}")
    cmd = ["ffmpeg", "-y", "-i", input_path, output_path]
    try:
        ffprogress.run(cmd, task_name="Extracting Cover.", print_errors=False)
    except RuntimeError:
        print("[yellow]Warning:[/] Unable to extract cover.")
