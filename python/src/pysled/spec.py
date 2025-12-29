"""Shared types and constants."""

import string
from types import MappingProxyType
from typing import Dict, FrozenSet, List, Literal, Mapping, Union


# Sled type groups

Concrete = Union[str, bytes, float, int, bool, None]
"""These can be a key in a map."""

Entity = Union[
    Concrete,
    Dict[str, "Entity"],
    Dict[int, "Entity"],
    List["Entity"],
]
"""These can be a value in a `map` or element in a `list`."""


# General

EMPTY = ""
KEYWORD_MARK = "@"
KEYWORD_CHAR_SET = frozenset(f"{string.digits}{string.ascii_letters}_")
OPEN_PAREN = "("
CLOSE_PAREN = ")"

C0_CONTROL_SET = frozenset(chr(i) for i in range(32)).union((chr(127),))
"""32 C0 control characters, plus the DEL character."""


# `comment`

COMMENT_MARK = "#"

TAB_CHARACTER = "\t"

COMMENT_DISALLOWED_SYMBOLS = C0_CONTROL_SET.union(
    (EMPTY,),  # empty string indicates end of input
).difference(
    (TAB_CHARACTER,)  # tab character allowed
)
"""
In `comment`, of the 33 C0 control characters (including DEL),
only the tab character (ASCII decimal 9) is allowed.
Any line separator character indicate the end of the comment.
Additionally, the empty string is used to indicate the end of the input.
"""


# `ws`

LF_LINE_SEPARATOR: "LineSeparator" = "\n"
CR_LINE_SEPARATOR: "LineSeparator" = "\r"
CRLF_LINE_SEPARATOR: "LineSeparator" = "\r\n"

LineSeparator = Literal[
    LF_LINE_SEPARATOR, CR_LINE_SEPARATOR, CRLF_LINE_SEPARATOR
]

DEFAULT_LINE_SEPARATOR = LF_LINE_SEPARATOR

LINE_SEPARATOR_SET: FrozenSet[LineSeparator] = frozenset(LineSeparator.__args__)
HORIZONTAL_SPACE_SET = frozenset(" \t")
WS_SET = LINE_SEPARATOR_SET.union(HORIZONTAL_SPACE_SET)

DEFAULT_INDENT = "  "
"""Two spaces."""


# Container types: `map`, `list`

MAP_OPEN_MARK = "{"
MAP_CLOSE_MARK = "}"
LIST_OPEN_MARK = "["
LIST_CLOSE_MARK = "]"
DELIMITER_MARK = ";"
KEY_VALUE_SEPARATOR = "="

CONTAINER_SYMBOL_SET = frozenset(
    (
        DELIMITER_MARK,
        KEY_VALUE_SEPARATOR,
        MAP_OPEN_MARK, MAP_CLOSE_MARK,
        LIST_OPEN_MARK, LIST_CLOSE_MARK,
        "<", ">",
    )
)

_DELIMITER_MARK_TUP = (DELIMITER_MARK,)
DELIMITER_SET = LINE_SEPARATOR_SET.union(_DELIMITER_MARK_TUP)
DELIMITER_OR_HORIZONTAL_SPACE_SET = HORIZONTAL_SPACE_SET.union(_DELIMITER_MARK_TUP)


# Number: `integer`, `float`

SLED_INTEGER_MIN = -9223372036854775808  # -(2 ** 63)
SLED_INTEGER_MAX = 9223372036854775807  # 2 ** 63 - 1

SignType = Literal["-", "+"]
DecimalMarkType = Literal[".", ","]
ExponentPrefixType = Literal["E", "e"]

DIGIT_SEPARATOR = "_"
_DIGIT_SEPARATOR_TUP = (DIGIT_SEPARATOR,)

SIGN_SET: FrozenSet[SignType] = frozenset(SignType.__args__)
DIGIT_SET = frozenset(string.digits)
OPTIONAL_DIGIT_SET = DIGIT_SET.union(_DIGIT_SEPARATOR_TUP)
DECIMAL_MARK_SET: FrozenSet[DecimalMarkType] = frozenset(DecimalMarkType.__args__)
EXPONENT_PREFIX_SET: FrozenSet[ExponentPrefixType] = frozenset(ExponentPrefixType.__args__)
NUMBER_START_SET = OPTIONAL_DIGIT_SET.union(SIGN_SET, DECIMAL_MARK_SET)

DEFAULT_DECIMAL_MARK: DecimalMarkType = "."
DEFAULT_EXPONENT_PREFIX: ExponentPrefixType = "e"


# Binary: `hex`

HEX_KEYWORD_NAME = "hex"
HEX_OPEN_MARK = OPEN_PAREN
HEX_CLOSE_MARK = CLOSE_PAREN
HEX_DIGITS_PER_BYTE = 2

HEX_DIGIT_SET = frozenset(string.hexdigits).union(_DIGIT_SEPARATOR_TUP)
HEX_CHAR_SET = HEX_DIGIT_SET.union(HORIZONTAL_SPACE_SET, WS_SET)

DEFAULT_HEX_BYTES_PER_SEPARATOR = -2
DEFAULT_HEX_LINE_LENGTH = 80


# String: `identity`, `quote`, `concat`

SINGLE_QUOTE_MARK = "'"
DOUBLE_QUOTE_MARK = '"'
QuoteMarkType = Literal[SINGLE_QUOTE_MARK, DOUBLE_QUOTE_MARK]
QUOTE_MARK_SET: FrozenSet[QuoteMarkType] = frozenset(QuoteMarkType.__args__)
DEFAULT_QUOTE_MARK: QuoteMarkType = DOUBLE_QUOTE_MARK

CONCAT_KEYWORD_NAME = "concat"
CONCAT_OPEN_MARK = OPEN_PAREN
CONCAT_CLOSE_MARK = CLOSE_PAREN

ESCAPE_CHARACTER = "\\"

UNICODE_ESCAPE_KEY = "u"
UNICODE_ESCAPE_OPEN_MARK = "{"
UNICODE_ESCAPE_CLOSE_MARK = "}"
UNICODE_ESCAPE_OPEN_SEQUENCE = (
    f"{ESCAPE_CHARACTER}{UNICODE_ESCAPE_KEY}{UNICODE_ESCAPE_OPEN_MARK}"
)

SIMPLE_ESCAPE_EVALUATION: Mapping[str, str] = MappingProxyType({
    ESCAPE_CHARACTER: ESCAPE_CHARACTER,
    DOUBLE_QUOTE_MARK: DOUBLE_QUOTE_MARK,
    SINGLE_QUOTE_MARK: SINGLE_QUOTE_MARK,
    "n": LF_LINE_SEPARATOR,
    "r": CR_LINE_SEPARATOR,
    "t": TAB_CHARACTER,
})
"""
Evaluation for each escape sequence that denotes a single particular value
(all escape sequences except for Unicode).
"""

SIMPLE_ESCAPE_SEQUENCES: Mapping[str, str] = MappingProxyType({
    v: f"{ESCAPE_CHARACTER}{k}"
    for k, v in SIMPLE_ESCAPE_EVALUATION.items()
})
"""
Each escape sequence that denotes a single particular value
(all escape sequences except for Unicode).
"""

ESCAPE_CHARACTER_ESCAPE = SIMPLE_ESCAPE_SEQUENCES[ESCAPE_CHARACTER]
LF_LINE_SEPARATOR_ESCAPE = SIMPLE_ESCAPE_SEQUENCES[LF_LINE_SEPARATOR]
CR_LINE_SEPARATOR_ESCAPE = SIMPLE_ESCAPE_SEQUENCES[CR_LINE_SEPARATOR]

LINE_SEPARATOR_ESCAPES: Mapping[LineSeparator, str] = MappingProxyType({
    LF_LINE_SEPARATOR: LF_LINE_SEPARATOR_ESCAPE,
    CR_LINE_SEPARATOR: CR_LINE_SEPARATOR_ESCAPE,
    CRLF_LINE_SEPARATOR: f"{CR_LINE_SEPARATOR_ESCAPE}{LF_LINE_SEPARATOR_ESCAPE}",
})

C0_SIMPLE_ESCAPE_SET = frozenset(
    (LF_LINE_SEPARATOR, CR_LINE_SEPARATOR, TAB_CHARACTER)
)
"""
C0 control characters that have their own (non-Unicode) escape sequences.
"""

RESTRICTED_QUOTE_SYMBOLS = C0_CONTROL_SET.union(
    (ESCAPE_CHARACTER, EMPTY)
).difference(
    (TAB_CHARACTER,)  # tab character allowed
)
"""
In `quote`, of the 33 C0 control characters (including DEL),
only the tab character (ASCII decimal 9) is allowed.
(All line separators are disallowed.)
Use of the escape character is restricted to specific escape sequences.

In addition to these, single and double quote marks are restricted,
but that restriction is handled by custom logic elsewhere.
"""

IDENTITY_DISALLOWED_SYMBOLS = RESTRICTED_QUOTE_SYMBOLS.union(
    HORIZONTAL_SPACE_SET,
    QUOTE_MARK_SET,
    (ESCAPE_CHARACTER,),
    CONTAINER_SYMBOL_SET,
    (OPEN_PAREN, CLOSE_PAREN),
    (COMMENT_MARK,),
)
"""
Only a subset of the symbols allowed for `quote` are allowed for `identity`.
Additional restrictions include any horizontal space, both quote marks,
the backslash character, the comment mark, and other symbols reserved for
denoting structure in Sled.
"""

IDENTITY_DISALLOWED_START_SYMBOLS = IDENTITY_DISALLOWED_SYMBOLS.union(
    NUMBER_START_SET, (KEYWORD_MARK,)
)
"""
In addition to the restrictions that apply to all `identity` symbols,
`identity` cannot start with any other symbol that a different `entity`
may start with, such as the keyword mark (`@`).

This includes all digits (`0` to `9`), signs (`+` and `-`),
decimal marks (`.` and `,`), and the digit separator (`_`), since a `float`
(and for some, an `integer`) may start with these.
"""
