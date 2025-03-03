# Standard Library

# Third Party
from lark import Transformer

# Local


class FFMetadataTransformer(Transformer):
    """Transforms a Lark parse tree into a dictionary of metadata items and chapters."""
    def __init__(self):
        self.chapters = list()
        self.global_data = dict()

    def metadata(self, data):
        """Split the global metadata from the chapters."""
        for item in data:
            if isinstance(item, dict):
                self.chapters.append(item)
            else:
                self.global_data[item[0]] = item[1]
        return {"global": self.global_data, "chapters": self.chapters}
    chapter = dict
    data = tuple
    KEY = str
    VALUE = str


FFMETADATA_GRAMMAR = r"""
?metadata: _WS* _HEADER _WS* data* chapter*
chapter: _CHAPTER_MARKER _WS* data*
data: KEY _EQUAL_SIGN VALUE _WS*
KEY: /[^\s=]+/
VALUE: /[^\n]+/

_HEADER: ";FFMETADATA1"i
_CHAPTER_MARKER: "[CHAPTER]"i
_EQUAL_SIGN: "="

_NEWLINE: NEWLINE
_WS: WS
%import common.NEWLINE
%import common.WS
"""

FFMETADATA_TERMINATOR_FRIENDLY_NAMES = {
    "_HEADER": "Header (ie. ';FFMETADATA1')",
    "_CHAPTER_MARKER": "Chapter Marker (ie. '[CHAPTER]')",
    "_EQUAL_SIGN": "Equal Sign (ie. '=')",
    "KEY": "Metadata item name",
    "VALUE": "Metadata item value",
    "_NEWLINE": "<New Line>",
    "_WS": "<Whitespace>",
}
