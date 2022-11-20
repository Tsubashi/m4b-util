from m4b_util.helpers import ffprobe


def check_output_folder(output_path, expected_files=None, check_func=None):
    """Check that expected output exists.

    :param output_path: Path to the directory to check.
    :param expected_files: Files we expect to find in output_path. If unspecified, defaults to ["segment_0000.mp3"].
    :param check_func: Function for checking each file in expected_files. Defaults to asserting ffprobe can read them.

    """
    # Default check function, in case one isn't passed in.
    def default_check(input_file_path):
        """Ensure ffprobe can read the file."""
        # Add in filename to make any failure more legible
        assert input_file_path.name and ffprobe.run_probe(input_file_path)

    # Set defaults
    if expected_files is None:
        expected_files = ["segment_0000.mp3"]
    if not check_func:
        check_func = default_check

    # Check the output
    for file_name in expected_files:
        file_path = output_path / file_name
        check_func(file_path)

    # Make sure there aren't any extra files in the directory
    for file in output_path.glob("*"):
        assert (file.name in expected_files)


def assert_file_path_is_file(input_file_path):
    """Ensure each file exists and is a file."""
    assert input_file_path.is_file()
