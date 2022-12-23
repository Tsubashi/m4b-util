"""Fixtures for expected data."""
from pathlib import Path

import pytest

from m4b_util.helpers import SegmentData


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
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=5000\ntitle=1\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=5000\nEND=10000\ntitle=2\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=10000\nEND=15000\ntitle=3\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=15000\nEND=20000\ntitle=4\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=20000\nEND=25000\ntitle=5\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=25000\nEND=30000\ntitle=6\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=30000\nEND=35000\ntitle=7\n'
                         '[CHAPTER]\nTIMEBASE=1/1000\nSTART=35000\nEND=40000\ntitle=8\n'
                         ),
            "chapters": [
                SegmentData(start_time=00., end_time=05., id=1, title="1", backing_file=Path("1 - 110Hz")),
                SegmentData(start_time=05., end_time=10., id=2, title="2", backing_file=Path("2 - 220Hz")),
                SegmentData(start_time=10., end_time=15., id=3, title="3", backing_file=Path("3 - 330Hz")),
                SegmentData(start_time=15., end_time=20., id=4, title="4", backing_file=Path("4 - 440Hz")),
                SegmentData(start_time=20., end_time=25., id=5, title="5", backing_file=Path("5 - 550Hz")),
                SegmentData(start_time=25., end_time=30., id=6, title="6", backing_file=Path("6 - 660Hz")),
                SegmentData(start_time=30., end_time=35., id=7, title="7", backing_file=Path("7 - 770Hz")),
                SegmentData(start_time=35., end_time=40., id=8, title="8", backing_file=Path("8 - 880Hz"))
            ],
            "chapters_doubled": [
                SegmentData(start_time=00., end_time=05., id=1, title="1", backing_file=Path("1 - 110Hz")),
                SegmentData(start_time=05., end_time=10., id=2, title="2", backing_file=Path("2 - 220Hz")),
                SegmentData(start_time=10., end_time=15., id=3, title="3", backing_file=Path("3 - 330Hz")),
                SegmentData(start_time=15., end_time=20., id=4, title="4", backing_file=Path("4 - 440Hz")),
                SegmentData(start_time=20., end_time=25., id=5, title="5", backing_file=Path("5 - 550Hz")),
                SegmentData(start_time=25., end_time=30., id=6, title="6", backing_file=Path("6 - 660Hz")),
                SegmentData(start_time=30., end_time=35., id=7, title="7", backing_file=Path("7 - 770Hz")),
                SegmentData(start_time=35., end_time=40., id=8, title="8", backing_file=Path("8 - 880Hz")),
                SegmentData(start_time=40., end_time=45., id=9, title="9", backing_file=Path("1 - 110Hz")),
                SegmentData(start_time=45., end_time=50., id=10, title="10", backing_file=Path("2 - 220Hz")),
                SegmentData(start_time=50., end_time=55., id=11, title="11", backing_file=Path("3 - 330Hz")),
                SegmentData(start_time=55., end_time=60., id=12, title="12", backing_file=Path("4 - 440Hz")),
                SegmentData(start_time=60., end_time=65., id=13, title="13", backing_file=Path("5 - 550Hz")),
                SegmentData(start_time=65., end_time=70., id=14, title="14", backing_file=Path("6 - 660Hz")),
                SegmentData(start_time=70., end_time=75., id=15, title="15", backing_file=Path("7 - 770Hz")),
                SegmentData(start_time=75., end_time=80., id=16, title="16", backing_file=Path("8 - 880Hz"))
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
                SegmentData(start_time=00.00, end_time=05.04, id=1, title="1", backing_file=Path("1 - 110Hz")),
                SegmentData(start_time=05.04, end_time=10.08, id=2, title="2", backing_file=Path("2 - 220Hz")),
                SegmentData(start_time=10.08, end_time=15.12, id=3, title="3", backing_file=Path("3 - 330Hz")),
                SegmentData(start_time=15.12, end_time=20.16, id=4, title="4", backing_file=Path("4 - 440Hz")),
                SegmentData(start_time=20.16, end_time=25.20, id=5, title="5", backing_file=Path("5 - 550Hz")),
                SegmentData(start_time=25.20, end_time=30.24, id=6, title="6", backing_file=Path("6 - 660Hz")),
                SegmentData(start_time=30.24, end_time=35.28, id=7, title="7", backing_file=Path("7 - 770Hz")),
                SegmentData(start_time=35.28, end_time=40.32, id=8, title="8", backing_file=Path("8 - 880Hz"))
            ],
            "chapters_doubled": [
                SegmentData(start_time=00.00, end_time=05.04, id=1, title="1", backing_file=Path("1 - 110Hz")),
                SegmentData(start_time=05.04, end_time=10.08, id=2, title="2", backing_file=Path("2 - 220Hz")),
                SegmentData(start_time=10.08, end_time=15.12, id=3, title="3", backing_file=Path("3 - 330Hz")),
                SegmentData(start_time=15.12, end_time=20.16, id=4, title="4", backing_file=Path("4 - 440Hz")),
                SegmentData(start_time=20.16, end_time=25.20, id=5, title="5", backing_file=Path("5 - 550Hz")),
                SegmentData(start_time=25.20, end_time=30.24, id=6, title="6", backing_file=Path("6 - 660Hz")),
                SegmentData(start_time=30.24, end_time=35.28, id=7, title="7", backing_file=Path("7 - 770Hz")),
                SegmentData(start_time=35.28, end_time=40.32, id=8, title="8", backing_file=Path("8 - 880Hz")),
                SegmentData(start_time=40.32, end_time=45.36, id=9, title="9", backing_file=Path("1 - 110Hz")),
                SegmentData(start_time=45.36, end_time=50.40, id=10, title="10", backing_file=Path("2 - 220Hz")),
                SegmentData(start_time=50.40, end_time=55.44, id=11, title="11", backing_file=Path("3 - 330Hz")),
                SegmentData(start_time=55.44, end_time=60.48, id=12, title="12", backing_file=Path("4 - 440Hz")),
                SegmentData(start_time=60.48, end_time=65.52, id=13, title="13", backing_file=Path("5 - 550Hz")),
                SegmentData(start_time=65.52, end_time=70.56, id=14, title="14", backing_file=Path("6 - 660Hz")),
                SegmentData(start_time=70.56, end_time=75.60, id=15, title="15", backing_file=Path("7 - 770Hz")),
                SegmentData(start_time=75.60, end_time=80.64, id=16, title="16", backing_file=Path("8 - 880Hz"))
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
                SegmentData(start_time=00.00, end_time=05.04, id=1, title="1 - 110Hz", backing_file=Path("1 - 110Hz")),
                SegmentData(start_time=05.04, end_time=10.08, id=2, title="2 - 220Hz", backing_file=Path("2 - 220Hz")),
                SegmentData(start_time=10.08, end_time=15.12, id=3, title="3 - 330Hz", backing_file=Path("3 - 330Hz")),
                SegmentData(start_time=15.12, end_time=20.16, id=4, title="4 - 440Hz", backing_file=Path("4 - 440Hz")),
                SegmentData(start_time=20.16, end_time=25.20, id=5, title="5 - 550Hz", backing_file=Path("5 - 550Hz")),
                SegmentData(start_time=25.20, end_time=30.24, id=6, title="6 - 660Hz", backing_file=Path("6 - 660Hz")),
                SegmentData(start_time=30.24, end_time=35.28, id=7, title="7 - 770Hz", backing_file=Path("7 - 770Hz")),
                SegmentData(start_time=35.28, end_time=40.32, id=8, title="8 - 880Hz", backing_file=Path("8 - 880Hz"))
            ]
        },
        "chaptered": {
            "metadata": (";FFMETADATA1\nmajor_brand=M4A\nminor_version=512\ncompatible_brands=M4A isomiso2\n"
                         "title=Chaptered Audio\nartist=m4b-util\nalbum=Chaptered Audio\ndate=2022\ngenre=Audiobook\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=2500\ntitle=110Hz - Loud\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=2500\nEND=5000\ntitle=110Hz - Soft\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=5000\nEND=7500\ntitle=220Hz - Loud\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=7500\nEND=10000\ntitle=220Hz - Soft\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=10000\nEND=12500\ntitle=330Hz - Loud\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=12500\nEND=15000\ntitle=330Hz - Soft\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=15000\nEND=17500\ntitle=440Hz - Loud\n"
                         "[CHAPTER]\nTIMEBASE=1/1000\nSTART=17500\nEND=19999\ntitle=440Hz - Soft\n"
                         ),
            "chapters": [
                SegmentData(start_time=0.0, end_time=2.5, id=0,
                            title='110Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=0.0, file_end_time=2.5),
                SegmentData(start_time=2.5, end_time=5.0, id=1,
                            title='110Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=2.5, file_end_time=5.0),
                SegmentData(start_time=5.0, end_time=7.5, id=2,
                            title='220Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=5.0, file_end_time=7.5),
                SegmentData(start_time=7.5, end_time=10.0, id=3,
                            title='220Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=7.5, file_end_time=10.0),
                SegmentData(start_time=10.0, end_time=12.5, id=4,
                            title='330Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=10.0, file_end_time=12.5),
                SegmentData(start_time=12.5, end_time=15.0, id=5,
                            title='330Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=12.5, file_end_time=15.0),
                SegmentData(start_time=15.0, end_time=17.5, id=6,
                            title='440Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=15.0, file_end_time=17.5),
                SegmentData(start_time=17.5, end_time=19.999, id=7,
                            title='440Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=17.5, file_end_time=19.999)
            ],
            "chapters_doubled": [
                SegmentData(start_time=0.0, end_time=2.5, id=0,
                            title='110Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=0.0, file_end_time=2.5),
                SegmentData(start_time=2.5, end_time=5.0, id=1,
                            title='110Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=2.5, file_end_time=5.0),
                SegmentData(start_time=5.0, end_time=7.5, id=2,
                            title='220Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=5.0, file_end_time=7.5),
                SegmentData(start_time=7.5, end_time=10.0, id=3,
                            title='220Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=7.5, file_end_time=10.0),
                SegmentData(start_time=10.0, end_time=12.5, id=4,
                            title='330Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=10.0, file_end_time=12.5),
                SegmentData(start_time=12.5, end_time=15.0, id=5,
                            title='330Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=12.5, file_end_time=15.0),
                SegmentData(start_time=15.0, end_time=17.5, id=6,
                            title='440Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=15.0, file_end_time=17.5),
                SegmentData(start_time=17.5, end_time=19.999, id=7,
                            title='440Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=17.5, file_end_time=19.999),
                SegmentData(start_time=19.999, end_time=22.499, id=8,
                            title='110Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=0.0, file_end_time=2.5),
                SegmentData(start_time=22.499, end_time=24.999, id=9,
                            title='110Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=2.5, file_end_time=5.0),
                SegmentData(start_time=24.999, end_time=27.499, id=10,
                            title='220Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=5.0, file_end_time=7.5),
                SegmentData(start_time=27.499, end_time=29.999, id=11,
                            title='220Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=7.5, file_end_time=10.0),
                SegmentData(start_time=29.999, end_time=32.499, id=12,
                            title='330Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=10.0, file_end_time=12.5),
                SegmentData(start_time=32.499, end_time=34.999, id=13,
                            title='330Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=12.5, file_end_time=15.0),
                SegmentData(start_time=34.999, end_time=37.499, id=14,
                            title='440Hz - Loud', backing_file=Path('chaptered_audio'),
                            file_start_time=15.0, file_end_time=17.5),
                SegmentData(start_time=37.499, end_time=39.998, id=15,
                            title='440Hz - Soft', backing_file=Path('chaptered_audio'),
                            file_start_time=17.5, file_end_time=19.999),
            ],
        }
    }
