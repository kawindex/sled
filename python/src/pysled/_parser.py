"""
Parse a Sled `document` into a Python `dict` by calling `from_sled`.

```python
sled_text = '''
name = "John Doe"
age = 50
children = [Jane; Jimmy]
'''

data = from_sled(sled_text)

assert data == {
    "name": "John Doe",
    "age": 50,
    "children": ["Jane", "Jimmy"],
}
```
"""

import math
from typing import (
    Callable, Container, Dict, List, Literal, Optional, Tuple, Union
)

from pysled._parser_metadata import ParseSnapshot, SledType
from pysled._sled_error import SledError, SledErrorCategory
from pysled._keyword_literal import KEYWORD_LITERALS
from pysled.spec import (
    COMMENT_DISALLOWED_SYMBOLS,
    COMMENT_MARK,
    CONCAT_CLOSE_MARK,
    CONCAT_KEYWORD_NAME,
    CONCAT_OPEN_MARK,
    CR_LINE_SEPARATOR,
    CRLF_LINE_SEPARATOR,
    DECIMAL_MARK_SET,
    DEFAULT_DECIMAL_MARK,
    DEFAULT_LINE_SEPARATOR,
    DELIMITER_MARK,
    DELIMITER_OR_HORIZONTAL_SPACE_SET,
    DELIMITER_SET,
    DIGIT_SEPARATOR,
    IDENTITY_DISALLOWED_START_SYMBOLS,
    IDENTITY_DISALLOWED_SYMBOLS,
    EMPTY,
    ESCAPE_CHARACTER,
    SIMPLE_ESCAPE_EVALUATION,
    EXPONENT_PREFIX_SET,
    HEX_CHAR_SET,
    HEX_CLOSE_MARK,
    HEX_DIGIT_SET,
    HEX_KEYWORD_NAME,
    HEX_OPEN_MARK,
    HORIZONTAL_SPACE_SET,
    KEYWORD_MARK,
    KEYWORD_CHAR_SET,
    KEY_VALUE_SEPARATOR,
    LIST_OPEN_MARK,
    LIST_CLOSE_MARK,
    MAP_OPEN_MARK,
    MAP_CLOSE_MARK,
    NUMBER_START_SET,
    OPTIONAL_DIGIT_SET,
    QUOTE_MARK_SET,
    RESTRICTED_QUOTE_SYMBOLS,
    SIGN_SET,
    SLED_INTEGER_MIN,
    SLED_INTEGER_MAX,
    UNICODE_ESCAPE_CLOSE_MARK,
    UNICODE_ESCAPE_KEY,
    UNICODE_ESCAPE_OPEN_MARK,
    Entity,
    SignType,
)


_INVALID_NUMBER_COEFFICIENT_ERROR_REASON = (
    "Invalid number. Expected at least 1 digit excluding any exponent."
)


def from_sled(text: str) -> Dict[str, Entity]:
    """
    Parse the input text into a Python `dict`.

    The input text should be a valid Sled `document`.
    Otherwise, raises an `InvalidSledError`.
    """

    parser = Parser(text)
    return parser.parse()


class Parser:
    """Basic recursive descent parser for Sled."""

    _text: str
    """
    Internal memory of the input text with all line separators standardized
    to `DEFAULT_LINE_SEPARATOR`.
    """

    _index: int
    """
    Tracks the current index within `self._text`.

    NOTE:
    Since we standardize all line separators to `DEFAULT_LINE_SEPARATOR`,
    the value of `self._index` is not guaranteed to be the real current index
    within the original input text, so it should never be exposed
    to `pysled` users (e.g. in error messages).
    """

    _line_num: int
    """
    Line number (within the text) of the current line.
    
    NOTE:
    This is 1-indexed in line with the convention used by many compilers
    and text editors, unlike (probably) every other index in this package,
    hence 'line_num' instead of 'line_index'.
    """

    _line_start: int
    """Start index (0-indexed within the input text) of the current line."""

    _evaluation: Optional[Dict[str, Entity]]
    """Cached result of parsing the input text."""

    def __init__(self, text: str) -> None:
        # Standardize to default line separator for ease of numbering lines
        self._text = standardize_line_separator(text)

        self._index = 0
        self._line_num = 1
        self._line_start = 0
        self._evaluation: Optional[Dict[str, Entity]] = None

    def reset(self) -> None:
        self._index = 0
        self._line_start = 0
        self._line_num = 1
        self._evaluation = None

    def parse(self) -> Dict[str, Entity]:
        if self._evaluation is None:
            self._evaluation = self._parse_document()
        return self._evaluation

    def _parse_document(self) -> Dict[str, Entity]:
        """
        Parse the input text as a standalone Sled document.
        This is the entry point to all of the internal parsing implementation.
        """

        has_top_level_braces = self._peek() == MAP_OPEN_MARK
        if has_top_level_braces:
            self._advance()

        evaluation = self._parse_map_content(key_type=SledType.STRING)
        self._consume_optional_ws_or_delimiters()

        if has_top_level_braces:
            # Validate and consume close brace
            if self._peek() == MAP_CLOSE_MARK:
                self._advance()
            else:
                raise self._make_invalid_sled_error(
                    f"Expected '{MAP_CLOSE_MARK}' to end top-level map "
                    f"but got {repr(self._peek())}."
                )

        if self._is_at_end():
            # Validate end of text
            return evaluation
        else:
            raise self._make_invalid_sled_error(
                "Sled input did not end where expected."
            )

    # Input interface

    def _is_at_end(self) -> bool:
        return self._index == len(self._text)

    def _peek(self) -> str:
        try:
            return self._text[self._index]
        except IndexError:
            if self._is_at_end():
                return EMPTY
            else:
                raise

    def _advance(self) -> None:
        self._index += 1

    def _next(self) -> str:
        self._index += 1
        return self._peek()

    def _get_range(self, start_index: int, end_index: int) -> str:
        """
        Returns the substring of the input text specified by the given indices.
        Does NOT validate index bounds. If either index is out of bounds,
        silently truncates the output; if both are, returns an empty string.
        Includes `start_index`, excludes `end_index`.
        """

        return self._text[start_index:end_index]

    # Error reporting

    def _make_invalid_sled_error(
        self,
        reason: str,
        *,
        error_category: SledErrorCategory = SledErrorCategory.SYNTAX,
        start_index: Optional[int] = None,
        end_index: Optional[int] = None,
        line_start: Optional[int] = None,
        line_num: Optional[int] = None,
    ) -> SledError:
        """
        Internal convenience function to instantiate an `InvalidSledError`.

        Since this is only expected to run when raising an `InvalidSledError`,
        it is not intended to be efficient.

        Args:
            reason:
                Why the identified part cannot be parsed as valid Sled.
                This should be a continuous line of text in sentence case.
            error_category:
                Category that the error belongs to.
            start_index:
                Start index (0-indexed within the input text, inclusive)
                of the part identified as invalid. Should be on the same line
                as `end_index`. If `None`, set to `self._index`.
            end_index:
                End index (0-indexed within the input text, exclusive)
                of the part identified as invalid. Should be on the same line
                as `start_index`. If `None`, set to `start_index + 1`.
            line_start:
                Start index (0-indexed within the input text, inclusive)
                of the line that contains the part identified as invalid.
                If `None`, set to `self._line_start`.
            line_num:
                Line number (within the text) of the line containing
                the part identified as invalid. This is 1-indexed in line with
                the convention used by many compilers and text editors,
                unlike (probably) every other index in this package,
                hence 'line_num' instead of 'line_index'.
                If `None`, set to `self._line_num`.
        """

        # Handle defaults
        if start_index is None:
            start_index = self._index
        if end_index is None:
            end_index = start_index + 1
        if line_start is None:
            line_start = self._line_start
        if line_num is None:
            line_num = self._line_num

        # Validation
        if not (line_start <= start_index < end_index <= len(self._text) + 1):
            raise ValueError(
                "At least one invalid index given when specifying "
                f"the location of the invalid Sled input. line_num={line_num} "
                f"line_start={line_start}, start_index={start_index}, "
                f"end_index={end_index}, text_length={len(self._text)}"
            )

        if self._text.find(
            DEFAULT_LINE_SEPARATOR, start_index, end_index - 1
        ) != -1:
            invalid_substring = self._get_range(start_index, end_index)
            raise ValueError(
                "The invalid substring specified should not contain "
                "any line separators except as the last character: "
                f"{repr(invalid_substring)}"
            )

        line_end = self._find_line_end(line_start)
        return SledError.make_short_parse_error(
            reason=reason,
            error_category=error_category,
            line=self._get_range(line_start, line_end),
            line_num=line_num,
            start_index=start_index-line_start,
            end_index=end_index-line_start,
        )

    def _find_line_end(self, start_index: int) -> int:
        """
        Returns the index (within the stored `self._text`) of the end
        of the line that `start_index` (within the stored `self._text`) is on.
        If `start_index` is on the last line, this is `len(self._text)`.
        Otherwise, this is the index of the first line separator that comes
        after `start_index`.
        """

        line_end = self._text.find(DEFAULT_LINE_SEPARATOR, start_index)
        return len(self._text) if line_end == -1 else line_end

    # Misc parsing

    def _consume_optional_ws(self) -> str:
        """
        Consumes and returns any consecutive `ws`, including line separators
        and comments.
        """

        return self._multi_line_consume_optional(HORIZONTAL_SPACE_SET)

    def _consume_optional_ws_or_delimiters(self) -> str:
        """
        Consumes and returns any consecutive delimiters or `ws`,
        including line separators and comments.
        """

        return self._multi_line_consume_optional(
            DELIMITER_OR_HORIZONTAL_SPACE_SET
        )

    def _multi_line_consume_optional(
            self, horizontal_set: Container[str]
        ) -> str:
        """
        Consumes and returns line separators (including comments),
        in addition to any element(s) in the given `horizontal_set`.

        Args:
            horizontal_set:
                Elements to consume, excluding line separators (and comments).
                Every element must be a `str` of length 1 and must not be
                a line separator. Implementation of the `__in__` method
                should be optimized (constant time).
        """

        start_index = self._index
        while True:
            c = self._peek()
            if c == DEFAULT_LINE_SEPARATOR:
                self._consume_default_line_separators()
            elif c == COMMENT_MARK:
                self._parse_comment()
            elif c in horizontal_set:
                while self._next() in horizontal_set:
                    pass
            else:
                break

        return self._get_range(start_index, self._index)

    def _parse_comment(self) -> str:
        """
        Consumes a comment and all (at least 1) consecutive line separators
        that immediately follow, then returns the content of the comment.
        """

        if self._peek() != COMMENT_MARK:
            raise self._make_invalid_sled_error(
                f"Expected comment to start with '{COMMENT_MARK}', "
                f"but got {repr(self._peek())}."
            )

        content_start_index = self._index + 1
        while self._next() not in COMMENT_DISALLOWED_SYMBOLS:
            pass
        content = self._get_range(content_start_index, self._index)
        if not self._is_at_end():
            self._consume_default_line_separators()
        return content

    def _consume_default_line_separators(self) -> str:
        """
        Consumes and returns all consecutive occurrences (at least 1)
        of the `DEFAULT_LINE_SEPARATOR`, handling state updates.
        """

        if self._peek() != DEFAULT_LINE_SEPARATOR:
            if self._is_at_end():
                return ""
            else:
                raise self._make_invalid_sled_error(
                    f"Expected {repr(DEFAULT_LINE_SEPARATOR)}, "
                    f"but got {repr(self._peek())}."
                )

        start_index = self._index
        while self._next() == DEFAULT_LINE_SEPARATOR:
            pass
        self._line_num += self._index - start_index
        self._line_start = self._index
        return self._get_range(start_index, self._index)

    # `container` types

    def _parse_entity(self) -> Entity:
        """Entry point for each value in a `map` or element in a `list`."""

        c = self._peek()
        if c == MAP_OPEN_MARK:
            self._advance()
            content = self._parse_map_content()
            if self._peek() == MAP_CLOSE_MARK:
                self._advance()
                return content
            else:
                raise self._make_invalid_sled_error(
                    f"Expected '{MAP_CLOSE_MARK}' to end map, "
                    f"but got {repr(self._peek())}."
                )
        elif c == LIST_OPEN_MARK:
            self._advance()
            content = self._parse_list_content()
            if self._peek() == LIST_CLOSE_MARK:
                self._advance()
                return content
            else:
                raise self._make_invalid_sled_error(
                    f"Expected '{LIST_CLOSE_MARK}' to end list, "
                    f"but got {repr(self._peek())}."
                )
        elif c == KEYWORD_MARK:
            keyword_evaluation, _ = self._parse_keyword()
            return keyword_evaluation
        elif c == NUMBER_START_SET:
            number_evaluation, _ = self._parse_number_excl_keyword()
            return number_evaluation
        elif c in QUOTE_MARK_SET:
            quote_evaluation, _ = self._parse_quote()
            return quote_evaluation
        elif c not in IDENTITY_DISALLOWED_START_SYMBOLS:
            identity_evaluation, _ = self._parse_identity()
            return identity_evaluation
        else:
            raise self._make_invalid_sled_error(
                f"Invalid entity. No entity starts with {repr(c)}."
            )

    def _parse_map_content(
        self, key_type: Optional[SledType] = None
    ) -> Union[Dict[str, Entity], Dict[int, Entity]]:
        """
        Parses key-value pairs. Checks for duplicate keys
        (after evaluation of each key as a Python `object`). 
        """

        start_index_within_line = self._index - self._line_start
        start_line_num = self._line_num
        self._consume_optional_ws_or_delimiters()
        c = self._peek()
        if c == MAP_CLOSE_MARK or c == "":
            return {}

        # Resolve key_parse_func.
        # If key_type is None, this entails parsing the first key,
        # For consistency, we just parse the first map pair in all cases.
        key, key_snapshot, key_parse_func = self._handle_map_first_key(key_type)
        data: List[Tuple[Union[int, str], ParseSnapshot, Entity]] = [
            (key, key_snapshot, self._parse_map_pair_after_key())
        ]

        # Collect remaining map pairs.
        while True:
            ws = self._consume_optional_ws_or_delimiters()
            c = self._peek()
            if c == MAP_CLOSE_MARK or c == "":
                break
            if DELIMITER_SET.isdisjoint(ws):
                raise self._make_invalid_sled_error(
                    f"Expected either the end of the map, or a delimiter "
                    f"('{DELIMITER_MARK}' or a line separator) before "
                    f"the next key-value pair, but got {repr(c)}."
                )
            key, key_snapshot = key_parse_func()
            data.append((key, key_snapshot, self._parse_map_pair_after_key()))

        # Validation: Check for duplicate keys.
        seen_keys = set()
        for k, _, _ in data:
            if k in seen_keys:
                raise SledError.make_duplicate_map_key_error(
                    data=[(k, snapshot) for k, snapshot, _ in data],
                    start_line_num=start_line_num,
                    start_index_within_line=start_index_within_line,
                )
            else:
                seen_keys.add(k)

        return {k: v for k, _, v in data}

    def _handle_map_first_key(
        self, key_type: Optional[SledType] = None
    ) -> Union[
        Tuple[str, ParseSnapshot, Callable[[], Tuple[str, ParseSnapshot]]],
        Tuple[int, ParseSnapshot, Callable[[], Tuple[int, ParseSnapshot]]],
    ]:
        if key_type is None:
            # Determine key_parse_func based on first key
            key, key_snapshot = self._parse_map_key()
            if key_snapshot.sled_type == SledType.STRING:
                return key, key_snapshot, self._parse_string
            elif key_snapshot.sled_type == SledType.INTEGER:
                return key, key_snapshot, self._parse_integer
            else:
                reason = (
                    "Expected map key to be either a string or integer, "
                    f"but got: {key_snapshot.sled_type}"
                )
                raise self._make_invalid_sled_error(
                    reason=reason,
                    error_category=SledErrorCategory.MAP_KEY_TYPE,
                    start_index=key_snapshot.start_index,
                    end_index=key_snapshot.end_index,
                    line_start=key_snapshot.line_start,
                    line_num=key_snapshot.line_num,
                )
        elif key_type == SledType.STRING:
            key, key_snapshot = self._parse_string()
            return key, key_snapshot, self._parse_string
        elif key_type == SledType.INTEGER:
            key, key_snapshot = self._parse_integer()
            return key, key_snapshot, self._parse_integer
        else:
            raise ValueError(
                "key_type must be SledType.STRING, SledType.INTEGER, "
                f"or None, but got: {key_type}"
            )

    def _parse_map_pair_after_key(self) -> Entity:
        self._consume_optional_ws()
        if self._peek() != KEY_VALUE_SEPARATOR:
            raise self._make_invalid_sled_error(
                f"Expected '{KEY_VALUE_SEPARATOR}' between key and value, "
                f"but got {repr(self._peek())}."
            )
        self._advance()
        self._consume_optional_ws()
        return self._parse_entity()

    def _parse_list_content(self) -> List[Entity]:
        """Parses each element within a `list`."""

        self._consume_optional_ws_or_delimiters()
        if self._peek() == LIST_CLOSE_MARK:
            return []

        content: List[Entity] = []
        while True:
            content.append(self._parse_entity())
            ws = self._consume_optional_ws_or_delimiters()
            if self._peek() == LIST_CLOSE_MARK:
                return content
            if DELIMITER_SET.isdisjoint(ws):
                raise self._make_invalid_sled_error(
                    f"Expected either '{LIST_CLOSE_MARK}' to end the list, "
                    f"or a delimiter ('{DELIMITER_MARK}' or a line separator) "
                    f"before the next entity, but got {repr(self._peek())}."
                )

    # Map keys

    def _parse_map_key(self) -> Tuple[Union[int, str], ParseSnapshot]:
        """Entry point for each key in a `map`."""

        start_index = self._index
        c = self._peek()
        if c == KEYWORD_MARK:
            self._advance()
            keyword_name, keyword_snapshot = self._parse_keyword_name()
            if keyword_name != CONCAT_KEYWORD_NAME:
                reason = (
                    "Expected a map key, but got a non-concat keyword: "
                    f"{self._get_range(start_index, self._index)}"
                )
                self._make_invalid_sled_error(
                    reason=reason,
                    start_index=start_index,
                    end_index=self._index,
                )
            return self._handle_concat_after_keyword(keyword_snapshot)
        elif c in NUMBER_START_SET:
            return self._parse_number_excl_keyword()
        elif c in QUOTE_MARK_SET:
            return self._parse_quote()
        elif c not in IDENTITY_DISALLOWED_START_SYMBOLS:
            return self._parse_identity()
        else:
            raise self._make_invalid_sled_error(
                f"Invalid map key. No map key starts with {repr(c)}."
            )

    def _parse_string(self) -> Tuple[str, ParseSnapshot]:
        start_index = self._index
        c = self._peek()
        if c == KEYWORD_MARK:
            self._advance()
            keyword_name, keyword_snapshot = self._parse_keyword_name()
            if keyword_name != CONCAT_KEYWORD_NAME:
                reason = (
                    "Expected a string, but got a non-concat keyword: "
                    f"{self._get_range(start_index, self._index)}"
                )
                self._make_invalid_sled_error(
                    reason=reason,
                    start_index=start_index,
                    end_index=self._index,
                )
            return self._handle_concat_after_keyword(keyword_snapshot)
        elif c in QUOTE_MARK_SET:
            return self._parse_quote()
        elif c not in IDENTITY_DISALLOWED_START_SYMBOLS:
            return self._parse_identity()
        else:
            raise self._make_invalid_sled_error(
                f"Invalid string. No string starts with {repr(c)}."
            )

    def _parse_integer(self) -> Tuple[int, ParseSnapshot]:
        start_index = self._start_index
        evaluation, parse_snapshot = self._parse_number_excl_keyword()
        if parse_snapshot.sled_type == SledType.INTEGER:
            return evaluation, parse_snapshot
        else:
            raise self._make_invalid_sled_error(
                f"Expected an integer, but got {parse_snapshot.sled_type}",
                start_index=start_index,
                end_index=self._index,
            )

    # Keywords

    def _parse_keyword(self) -> Tuple[
        Union[str, bytes, float, bool, None], ParseSnapshot
    ]:
        """
        Parses an `Entity` from a keyword.

        This includes any of the following:
        - `nil`: `@nil`
        - `boolean`: `@true`, `@false`
        - `float`: `@inf`, `@ninf`, `@nan`
        - `hex`: `@hex(...)`
        - `concat`: `@concat(...)`
        """

        # Validation
        if self._peek() != KEYWORD_MARK:
            raise self._make_invalid_sled_error(
                "Invalid keyword. Expected keyword to be prefixed "
                f"by '{KEYWORD_MARK}', but got {repr(self._peek())}."
            )

        start_index = self._index
        self._advance()
        keyword_name, keyword_snapshot = self._parse_keyword_name()

        # Keyword literal
        keyword_literal_spec = KEYWORD_LITERALS.get(keyword_name)
        if keyword_literal_spec is not None:
            return keyword_literal_spec.evaluation, keyword_snapshot

        # `hex`
        if keyword_name == HEX_KEYWORD_NAME:
            self._consume_optional_ws()
            if self._peek() != HEX_OPEN_MARK:
                raise self._make_invalid_sled_error(
                    f"Expected '{HEX_OPEN_MARK}' to start hex, "
                    f"but got {repr(self._peek())}."
                )
            self._advance()
            content = self._parse_hex_content()
            if self._peek() == HEX_CLOSE_MARK:
                self._advance()
                return content, ParseSnapshot(
                    start_index=keyword_snapshot.start_index,
                    end_index=self._index,
                    line_num=keyword_snapshot.line_num,
                    line_start=keyword_snapshot.line_start,
                    sled_type=SledType.HEX,
                )
            else:
                raise self._make_invalid_sled_error(
                    f"Expected '{HEX_CLOSE_MARK}' to end hex, "
                    f"but got {repr(self._peek())}."
                )

        # `concat`
        if keyword_name == CONCAT_KEYWORD_NAME:
            return self._handle_concat_after_keyword(keyword_snapshot)

        raise self._make_invalid_sled_error(
            reason=f'Invalid keyword "{KEYWORD_MARK}{keyword_name}".',
            start_index=start_index,
            end_index=self._index,
            line_start=self._line_start,
            line_num=self._line_num,
        )

    def _parse_keyword_name(self) -> Tuple[str, ParseSnapshot]:
        start_index = self._index
        if self._peek() in KEYWORD_CHAR_SET:
            while self._next() in KEYWORD_CHAR_SET:
                pass
        name = self._get_range(start_index, self._index)
        keyword_snapshot = ParseSnapshot(
            start_index=start_index,
            end_index=self._index,
            line_start=self._line_start,
            line_num=self._line_num,
            sled_type=None,
        )
        return name, keyword_snapshot

    def _parse_hex_content(self) -> bytes:
        content_start_index = self._index
        hex_close_index = self._text.find(
            HEX_CLOSE_MARK, content_start_index
        )
        if hex_close_index == -1:
            # Report first point of failure
            while self._next() in HEX_CHAR_SET:
                pass
            if self._is_at_end():
                raise self._make_invalid_sled_error(
                    "Invalid hex. Reached end of input without finding "
                    f"'{HEX_CLOSE_MARK}' to end hex."
                )
            else:
                raise self._make_invalid_sled_error(
                    f"Invalid hex. Expected only '{DIGIT_SEPARATOR}', "
                    f"hexadecimal and ws between '{HEX_OPEN_MARK}' and "
                    f"'{HEX_CLOSE_MARK}', but found {repr(self._peek())}."
                )

        content_str = self._get_range(content_start_index, hex_close_index)

        # Validate characters allowed
        content_set = frozenset(content_str)
        if not HEX_CHAR_SET.issuperset(content_set):
            # Report first invalid
            while self._next() in HEX_CHAR_SET:
                pass
            raise self._make_invalid_sled_error(
                f"Invalid hex. Expected only '{DIGIT_SEPARATOR}', "
                f"hexadecimal and ws between '{HEX_OPEN_MARK}' and "
                f"'{HEX_CLOSE_MARK}', but found {repr(self._peek())}."
            )

        # Filter for only hex digits
        for c in content_set.difference(HEX_DIGIT_SET):
            content_str = content_str.replace(c, "")

        # Validate full bytes (even number of hex digits)
        if len(content_str) % 2 != 0:
            reason = (
                "Invalid hex. Expected an even number of hexadecimal digits "
                f"for full bytes of data, but got {len(content_str)} "
                "hexadecimal digits."
            )
            raise self._make_invalid_sled_error(
                reason=reason,
                end_index=hex_close_index,
            )

        self._index = hex_close_index
        return bytes.fromhex(content_str)

    def _handle_concat_after_keyword(
        self, keyword_snapshot: ParseSnapshot
    ) -> Tuple[str, ParseSnapshot]:
        self._consume_optional_ws()
        if self._peek() != CONCAT_OPEN_MARK:
            raise self._make_invalid_sled_error(
                f"Expected '{CONCAT_OPEN_MARK}' to start concat, "
                f"but got {repr(self._peek())}."
            )
        self._advance()
        content = self._parse_concat_content()
        if self._peek() == CONCAT_CLOSE_MARK:
            self._advance()
            return content, ParseSnapshot(
                start_index=keyword_snapshot.start_index,
                end_index=self._index,
                line_num=keyword_snapshot.line_num,
                line_start=keyword_snapshot.line_start,
                sled_type=SledType.STRING,
            )
        else:
            raise self._make_invalid_sled_error(
                f"Expected '{CONCAT_CLOSE_MARK}' to end concat, "
                f"but got {repr(self._peek())}."
            )

    def _parse_concat_content(self) -> str:
        self._consume_optional_ws_or_delimiters()
        if self._peek() == CONCAT_CLOSE_MARK:
            return ""

        content: List[str] = []
        while True:
            if self._peek() not in QUOTE_MARK_SET:
                raise self._make_invalid_sled_error(
                    "Expected either a quote mark (single or double) "
                    f"to start a quote, or '{CONCAT_CLOSE_MARK}' "
                    f"to end the concat, but got {repr(self._peek())}."
                )
            quote, _ = self._parse_quote()
            content.append(quote)
            ws = self._consume_optional_ws_or_delimiters()
            if self._peek() == CONCAT_CLOSE_MARK:
                return "".join(content)
            if DELIMITER_SET.isdisjoint(ws):
                raise self._make_invalid_sled_error(
                    f"Expected either '{CONCAT_CLOSE_MARK}' to end "
                    f"the concat, or a delimiter ('{DELIMITER_MARK}' "
                    f"or a line separator) before the next segment, "
                    f"but got {repr(self._peek())}."
                )

    # Number types

    def _parse_number_excl_keyword(
        self
    ) -> Tuple[Union[int, float], ParseSnapshot]:
        """
        Parses an `integer` or a `float`, validating that its value is not
        one that should be represented by a keyword (`@inf`, `@ninf`, `@nan`).

        Both cannot start with the underscore (`_`), though it may appear
        at subsequent positions.
        """

        start_index = self._index
        sign_str = self._parse_optional_sign()

        coefficient_start_index = self._index
        raw_integral_str = self._consume_optional_digits()
        standardized_integral_str = remove_digit_separator(raw_integral_str)

        c = self._peek()
        if c not in DECIMAL_MARK_SET:
            # Decimal mark not encountered
            if len(standardized_integral_str) == 0:
                raise self._make_invalid_sled_error(
                    reason=_INVALID_NUMBER_COEFFICIENT_ERROR_REASON,
                    start_index=coefficient_start_index,
                    end_index=self._index,
                )
            if c in EXPONENT_PREFIX_SET:
                # `float`: no decimal, has exponent
                exponent_str = self._consume_exponent()
                parse_snapshot = ParseSnapshot(
                    start_index=start_index,
                    end_index=self._index,
                    line_num=self._line_num,
                    line_start=self._line_start,
                    sled_type=SledType.FLOAT,
                )
                evaluation = self._evaluate_float_excl_keyword(
                    f"{sign_str}{standardized_integral_str}{exponent_str}",
                    parse_snapshot,
                )
                return evaluation, parse_snapshot
            else:
                # `integer`: no decimal, no exponent
                parse_snapshot = ParseSnapshot(
                    start_index=start_index,
                    end_index=self._index,
                    line_num=self._line_num,
                    line_start=self._line_start,
                    sled_type=SledType.INTEGER,
                )
                integer_str = f"{sign_str}{standardized_integral_str}"
                evaluation = int(integer_str)

                # Validate within allowed values
                if (
                    evaluation < SLED_INTEGER_MIN
                    or SLED_INTEGER_MAX < evaluation
                ):
                    reason = (
                        "Invalid integer. Does not fall within allowed values "
                        f"for Sled integer (overflow): {integer_str}"
                    )
                    raise self._make_invalid_sled_error(
                        reason=reason,
                        error_category=SledErrorCategory.NUMBER_RANGE,
                        start_index=start_index,
                        end_index=self._index,
                    )

                return evaluation, parse_snapshot

        # Number contains a decimal mark

        # Consume mantissa
        self._advance()
        raw_mantissa_str = self._consume_optional_digits()
        standardized_mantissa_str = remove_digit_separator(raw_mantissa_str)

        if len(standardized_integral_str) == 0 and len(standardized_mantissa_str) == 0:
            raise self._make_invalid_sled_error(
                reason=_INVALID_NUMBER_COEFFICIENT_ERROR_REASON,
                start_index=coefficient_start_index,
                end_index=self._index,
            )

        # Optionally consume exponent
        exponent_str = ""
        if self._peek() in EXPONENT_PREFIX_SET:
            exponent_str = self._consume_exponent()

        parse_snapshot = ParseSnapshot(
            start_index=start_index,
            end_index=self._index,
            line_num=self._line_num,
            line_start=self._line_start,
            sled_type=SledType.FLOAT,
        )
        float_str = (
            f"{sign_str}{standardized_integral_str}"
            f"{DEFAULT_DECIMAL_MARK}{standardized_mantissa_str}{exponent_str}"
        )
        evaluation = self._evaluate_float_excl_keyword(
            float_str, parse_snapshot
        )
        return evaluation, parse_snapshot

    def _parse_optional_sign(self) -> Union[SignType, Literal[""]]:
        if self._peek() == DIGIT_SEPARATOR:
            while self._next() == DIGIT_SEPARATOR:
                pass
        c = self._peek()
        if c in SIGN_SET:
            self._advance()
            return c
        else:
            return ""

    def _consume_optional_digits(self) -> str:
        start_index = self._index
        if self._peek() in OPTIONAL_DIGIT_SET:
            while self._next() in OPTIONAL_DIGIT_SET:
                pass
        return self._get_range(start_index, self._index)

    def _consume_exponent(self) -> str:
        exponent_prefix = self._peek()
        if exponent_prefix not in EXPONENT_PREFIX_SET:
            raise self._make_invalid_sled_error(
                "Invalid exponent. Must start with 'e' or 'E', "
                f"but got {repr(self._peek())}."
            )
        self._advance()
        sign_str = self._parse_optional_sign()
        exponent_digit_str = remove_digit_separator(
            self._consume_optional_digits()
        )
        if len(exponent_digit_str) > 0:
            return f"{exponent_prefix}{sign_str}{exponent_digit_str}"
        else:
            reason = (
                "Invalid exponent. Expected at least 1 digit in the exponent "
                f"(after '{exponent_prefix}{sign_str}')."
            )
            raise self._make_invalid_sled_error(reason=reason)

    def _evaluate_float_excl_keyword(
        self, s: str, parse_snapshot: ParseSnapshot
    ) -> float:
        """
        Evaluates a `float`, then validates that its value is not
        one that should be represented by a keyword (`@inf`, `@ninf`, `@nan`).
        """
        try:
            evaluation = float(s)
        except Exception as e:
            reason = (
                "Invalid float. "
                f"Python's built-in failed to convert input: {s}"
            )
            raise self._make_invalid_sled_error(
                reason=reason,
                error_category=SledErrorCategory.NUMBER_RANGE,
                start_index=parse_snapshot.start_index,
                end_index=parse_snapshot.end_index,
                line_start=parse_snapshot.line_start,
                line_num=parse_snapshot.line_num,
            ) from e

        # Validate not keyword value
        if math.isinf(evaluation) or math.isnan(evaluation):
            reason = (
                "Invalid float. Expected a non-keyword value but "
                f"Python's built-in converted input to {evaluation}: {s}"
            )
            raise self._make_invalid_sled_error(
                reason=reason,
                error_category=SledErrorCategory.NUMBER_RANGE,
                start_index=parse_snapshot.start_index,
                end_index=parse_snapshot.end_index,
                line_start=parse_snapshot.line_start,
                line_num=parse_snapshot.line_num,
            )
        else:
            return evaluation

    # `string` representations

    def _parse_quote(self) -> Tuple[str, ParseSnapshot]:
        """
        Parses a `quote`, which may contain escape sequences.

        The backslash is used as an escape character and is itself
        produced by two consecutive backslash characters.

        The 32 characters in the C0 control range and the DEL character
        are all disallowed for `quote`. These must be escaped.

        Additionally, a `quote` cannot contain the quote mark
        by which it is itself enclosed (unless escaped).
        """

        quote_mark = self._peek()
        if quote_mark not in QUOTE_MARK_SET:
            raise self._make_invalid_sled_error(
                "Expected a quote mark (single or double) to start quote, "
                f"but got {repr(quote_mark)}. "
            )

        restricted_symbols = RESTRICTED_QUOTE_SYMBOLS.union(quote_mark)
        start_index = self._index
        self._advance()
        pieces: List[str] = []
        while True:
            piece_start_index = self._index
            if self._peek() not in restricted_symbols:
                while self._next() not in restricted_symbols:
                    pass
            pieces.append(self._get_range(piece_start_index, self._index))

            c = self._peek()
            if c == quote_mark:
                self._advance()
                break
            elif c == ESCAPE_CHARACTER:
                pieces.append(self._parse_escape_sequence())
            elif c == "":
                raise self._make_invalid_sled_error(
                    f"Reached end of file without finding {repr(quote_mark)}"
                    " to end quote."
                )
            else:
                raise self._make_invalid_sled_error(
                    f"Invalid quote. Found disallowed symbol {repr(c)}."
                )

        parse_snapshot = ParseSnapshot(
            start_index=start_index,
            end_index=self._index,
            line_num=self._line_num,
            line_start=self._line_start,
            sled_type=SledType.STRING,
        )
        return "".join(pieces), parse_snapshot

    def _parse_escape_sequence(self) -> str:
        """Parses an escape sequence within a `quote`."""

        # Validate escape symbol
        if self._peek() != ESCAPE_CHARACTER:
            raise self._make_invalid_sled_error(
                f"Invalid escape sequence. Expected '{ESCAPE_CHARACTER}' "
                f"to start the escape sequence, but got {repr(self._peek())}."
            )

        # Two-character escape sequences
        c = self._next()
        evaluation = SIMPLE_ESCAPE_EVALUATION.get(c)
        if evaluation is not None:
            self._advance()
            return evaluation

        # Unicode escape sequences
        if c == UNICODE_ESCAPE_KEY:
            return self._parse_unicode_escape_content()

        reason = (
            f"Invalid escape sequence. No escape sequence "
            f"has the escape character followed by {repr(c)}."
        )
        raise self._make_invalid_sled_error(
            reason=reason,
            start_index=self._index - 1,
            end_index=self._index + 1,
        )

    def _parse_unicode_escape_content(self) -> str:
        if self._next() != UNICODE_ESCAPE_OPEN_MARK:
            raise self._make_invalid_sled_error(
                f"Expected '{UNICODE_ESCAPE_OPEN_MARK}' after "
                f'"{ESCAPE_CHARACTER}{UNICODE_ESCAPE_KEY}", '
                f"but got {repr(self._peek())}."
            )

        content_start_index = self._index + 1
        content_end_index = self._text.find(
            UNICODE_ESCAPE_CLOSE_MARK, content_start_index
        )
        if content_end_index == -1:
            # Report first point of failure
            while self._next() in HEX_DIGIT_SET:
                pass
            if self._is_at_end():
                raise self._make_invalid_sled_error(
                    "Invalid Unicode escape sequence. "
                    "Reached end of input without finding "
                    f"'{UNICODE_ESCAPE_CLOSE_MARK}' to end "
                    "escape sequence for Unicode code point."
                )
            else:
                raise self._make_invalid_sled_error(
                    "Invalid Unicode escape sequence. "
                    "Expected only hexadecimal, "
                    f"but found {repr(self._peek())}."
                )

        code_point_str = self._get_range(
            content_start_index, content_end_index
        )
        if not HEX_DIGIT_SET.issuperset(code_point_str):
            # Report first point of failure
            while self._next() in HEX_DIGIT_SET:
                pass
            raise self._make_invalid_sled_error(
                "Invalid Unicode escape sequence. "
                "Expected only hexadecimal between "
                f"'{UNICODE_ESCAPE_OPEN_MARK}' and "
                f"'{UNICODE_ESCAPE_CLOSE_MARK}', "
                f"but found {repr(self._peek())}."
            )

        self._index = content_end_index + 1
        return chr(int(code_point_str, base=16))

    def _parse_identity(self) -> Tuple[str, ParseSnapshot]:
        """
        Parses an `identity`, which can only contain a subset
        of the symbols allowed for `quote`. Restrictions include
        any horizontal space, both quote marks, the backslash character,
        and other symbols reserved for denoting structure in Sled.

        In addition, while an `identity` can contain digits and other symbols
        that appear in numbers (`.`, `+`, `-`), it is not allowed to start
        with any of these.
        """

        # Validate start symbol
        if self._peek() in IDENTITY_DISALLOWED_START_SYMBOLS:
            raise self._make_invalid_sled_error(
                f"Invalid identity. Cannot start with {repr(self._peek())}."
            )

        start_index = self._index
        while self._next() not in IDENTITY_DISALLOWED_SYMBOLS:
            pass

        parse_snapshot = ParseSnapshot(
            start_index=start_index,
            end_index=self._index,
            line_num=self._line_num,
            line_start=self._line_start,
            sled_type=SledType.STRING,
        )
        return self._get_range(start_index, self._index), parse_snapshot


# Utility functions


def standardize_line_separator(s: str) -> str:
    """
    Replace all line separators with the `DEFAULT_LINE_SEPARATOR`,
    which is `LF_LINE_SEPARATOR = "\n"`.
    """
    return s.replace(CRLF_LINE_SEPARATOR, DEFAULT_LINE_SEPARATOR).replace(
        CR_LINE_SEPARATOR, DEFAULT_LINE_SEPARATOR
    )


def remove_digit_separator(s: str) -> str:
    """
    Removes every digit separator, which is the underscore (`_`).

    While Python's built-in `int()` and `float()` conversion functions
    both allow the underscore (`_`) in the input `str`,
    Sled is considerably more accepting than even those,
    so we first remove any underscore(s) before conversion.
    """
    return s.replace(DIGIT_SEPARATOR, "")
