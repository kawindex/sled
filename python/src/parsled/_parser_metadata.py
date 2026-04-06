from enum import Enum
from typing import NamedTuple, Optional


class SledType(Enum):
    NIL = "nil"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    HEX = "hex"
    STRING = "string"
    SMAP = "smap"
    IMAP = "imap"
    LIST = "list"

    def __str__(self) -> str:
        return self.value


class ParseSnapshot(NamedTuple):
    """Metadata from parsing"""
    start_index: int
    end_index: int
    line_start: int
    line_num: int
    sled_type: Optional[SledType] = None,
