"""Helper functions for running ffprobe."""
import json
from subprocess import run


class Probe:
    """Holds the results from an ffprobe run."""
    def __init__(self, ffprobe_output):
        """Set up attributes."""
        self.data = json.loads(ffprobe_output)
        self.streams = self.data.get('streams', None)
        self.audio = next(
            (stream for stream in self.data.get('streams', list()) if stream.get('codec_type') == 'audio'), None
        )
        self.format = self.data.get('format')
        self.tags = self.data.get('format', dict()).get('tags', None)
        self.chapters = self.data.get('chapters')


def run_probe(file):
    """Run ffprobe on the specified file and return a JSON representation of the output."""
    cmd = ["ffprobe", "-show_format", "-show_streams", "-show_chapters", "-of", "json", "-i", file]

    p = run(cmd, capture_output=True)
    if p.returncode != 0:
        return None
    return Probe(p.stdout.decode('utf-8'))
