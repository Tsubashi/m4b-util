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


def add_cover(input_path, cover_path, output_path):
    """Add a cover image to an audio file.

    :param input_path: What to add the cover to.
    :param cover_path: What cover to add.
    :param output_path: Where to put the new file.
    """
    cmd = ["ffmpeg", "-y", "-i", input_path, "-i", cover_path, "-map", "0:a", "-map", "1",
           "-c", "copy", "-disposition:v:0", "attached_pic", output_path]
    ffprogress.run(cmd, task_name="Adding Cover.", print_errors=False)
