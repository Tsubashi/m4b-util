"""Fixtures for expected data."""
import pytest


@pytest.fixture(scope='session')
def expected_data():
    """Dictionary of data expected after processing the tone files.

    For some reason, the mp3 timestamps are different from wav and m4a.
    """
    return {
        "default": {
            "metadata": (';FFMETADATA1\nmajor_brand=M4A\nminor_version=512\ncompatible_brands=M4A isomiso2\n'
                         'title=None\n'
                         'artist=None\n'
                         'album=None\n'
                         'date=None\n'
                         'genre=Audiobook\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=4999\ntitle=1\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=5000\nEND=9999\ntitle=2\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=10000\nEND=14999\ntitle=3\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=15000\nEND=19999\ntitle=4\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=20000\nEND=24999\ntitle=5\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=25000\nEND=29999\ntitle=6\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=30000\nEND=34999\ntitle=7\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=35000\nEND=39999\ntitle=8\n'
                         ),
            "chapters": [
                {'startTime': 0, 'title': 1},
                {'startTime': 5000, 'title': 2},
                {'startTime': 10000, 'title': 3},
                {'startTime': 15000, 'title': 4},
                {'startTime': 20000, 'title': 5},
                {'startTime': 25000, 'title': 6},
                {'startTime': 30000, 'title': 7},
                {'startTime': 35000, 'title': 8},
            ]
        },
        "mp3": {
            "metadata": (';FFMETADATA1\nmajor_brand=M4A\nminor_version=512\ncompatible_brands=M4A isomiso2\n'
                         'title=None\n'
                         'artist=None\n'
                         'album=None\n'
                         'date=None\n'
                         'genre=Audiobook\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=5039\ntitle=1\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=5040\nEND=10079\ntitle=2\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=10080\nEND=15119\ntitle=3\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=15120\nEND=20159\ntitle=4\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=20160\nEND=25199\ntitle=5\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=25200\nEND=30239\ntitle=6\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=30240\nEND=35279\ntitle=7\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=35280\nEND=40319\ntitle=8\n'
                         ),
            "chapters": [
                {'startTime': 0, 'title': 1},
                {'startTime': 5040, 'title': 2},
                {'startTime': 10080, 'title': 3},
                {'startTime': 15120, 'title': 4},
                {'startTime': 20160, 'title': 5},
                {'startTime': 25200, 'title': 6},
                {'startTime': 30240, 'title': 7},
                {'startTime': 35280, 'title': 8},
            ]
        },
        "use_filename": {
            "metadata": (';FFMETADATA1\nmajor_brand=M4A\nminor_version=512\ncompatible_brands=M4A isomiso2\n'
                         'title=None\n'
                         'artist=None\n'
                         'album=None\n'
                         'date=None\n'
                         'genre=Audiobook\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=5039\ntitle=1 - 110Hz\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=5040\nEND=10079\ntitle=2 - 220Hz\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=10080\nEND=15119\ntitle=3 - 330Hz\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=15120\nEND=20159\ntitle=4 - 440Hz\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=20160\nEND=25199\ntitle=5 - 550Hz\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=25200\nEND=30239\ntitle=6 - 660Hz\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=30240\nEND=35279\ntitle=7 - 770Hz\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=35280\nEND=40319\ntitle=8 - 880Hz\n'
                         ),
            "chapters": [
                {'startTime': 0, 'title': "1 - 110Hz"},
                {'startTime': 5040, 'title': "2 - 220Hz"},
                {'startTime': 10080, 'title': "3 - 330Hz"},
                {'startTime': 15120, 'title': "4 - 440Hz"},
                {'startTime': 20160, 'title': "5 - 550Hz"},
                {'startTime': 25200, 'title': "6 - 660Hz"},
                {'startTime': 30240, 'title': "7 - 770Hz"},
                {'startTime': 35280, 'title': "8 - 880Hz"},
            ]
        }
    }
