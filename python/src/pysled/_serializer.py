"""
This module provides 2 ways to serialize Python objects.
1. Call `to_sled()`.
2. Instantiate a `SledSerializer` and call its `to_sled()` method.

Both have the same configuration options and defaults.
Refer to their documentation for details.

Approach #1 simply does approach #2 under the hood.
Approach #2 may be useful if you want to set a configuration once
and reuse that for serialization multiple times.

```python
from pysled import SledSerializer, to_sled

data = {}
other_data = {}

# Approach #1
sled_output = to_sled(data)

# Approach #2
sled_serializer = SledSerializer()
sled_output = sled_serializer.to_sled(data)
other_sled_output = sled_serializer.to_sled(other_data)
```
"""

from typing import List, Literal

from pysled._serializer_basic import (
    DEFAULT_ALWAYS_QUOTE,
    DEFAULT_ASCII_ONLY,
    DEFAULT_HEX_UPPER_CASE,
    DEFAULT_USE_TOP_LEVEL_BRACES,
    SledSerializerBasic,
)
from pysled.spec import (
    CONCAT_KEYWORD_NAME,
    CONCAT_OPEN_MARK,
    CONCAT_CLOSE_MARK,
    DEFAULT_DECIMAL_MARK,
    DEFAULT_EXPONENT_PREFIX,
    DEFAULT_HEX_BYTES_PER_SEPARATOR,
    DEFAULT_HEX_LINE_LENGTH,
    DEFAULT_INDENT,
    DEFAULT_QUOTE_MARK,
    DEFAULT_LINE_SEPARATOR,
    DIGIT_SEPARATOR,
    HEX_CLOSE_MARK,
    HEX_DIGITS_PER_BYTE,
    HEX_KEYWORD_NAME,
    HEX_OPEN_MARK,
    KEYWORD_MARK,
    LineSeparator,
    DecimalMarkType,
    ExponentPrefixType,
    QuoteMarkType
)


HexHorizontalSeparator = Literal["", " ", "\t", DIGIT_SEPARATOR]
"""
In addition to the general Sled restriction that horizontal separators in `hex`
can contain only spaces, tabs and underscores, this `SledSerializer` limits
its length to at most 1 character.
"""

# Default settings
DEFAULT_BREAK_ON_LINE_SEPARATOR = True
DEFAULT_HEX_HORIZONTAL_SEPARATOR: HexHorizontalSeparator = DIGIT_SEPARATOR
DEFAULT_USE_THOUSANDS_SEPARATOR = True


def to_sled(
    obj: object,
    *,
    indent: str = DEFAULT_INDENT,
    use_top_level_braces: bool = DEFAULT_USE_TOP_LEVEL_BRACES,
    line_separator: LineSeparator = DEFAULT_LINE_SEPARATOR,
    # string
    always_quote: bool = DEFAULT_ALWAYS_QUOTE,
    break_on_line_separator: bool = DEFAULT_BREAK_ON_LINE_SEPARATOR,
    ascii_only: bool = DEFAULT_ASCII_ONLY,
    quote_mark: QuoteMarkType = DEFAULT_QUOTE_MARK,
    # hex
    hex_upper_case: bool = DEFAULT_HEX_UPPER_CASE,
    hex_horizontal_separator: HexHorizontalSeparator = DEFAULT_HEX_HORIZONTAL_SEPARATOR,
    hex_bytes_per_separator: int = DEFAULT_HEX_BYTES_PER_SEPARATOR,
    hex_line_length: int = DEFAULT_HEX_LINE_LENGTH,
    # float
    decimal_mark: DecimalMarkType = DEFAULT_DECIMAL_MARK,
    exponent_prefix: ExponentPrefixType = DEFAULT_EXPONENT_PREFIX,
    use_thousands_separator: bool = DEFAULT_USE_THOUSANDS_SEPARATOR,
) -> str:
    """
    Serializes the input `obj` as a (top level) Sled `document`.

    This function has the same configuration options and defaults
    as `SledSerializer`.
    For details, refer to the `SledSerializer` documentation.

    The input `obj` must be a `Mapping` or `dataclass` that does NOT have
    a `to_sled_serializable()` method, or an object with such a method
    returning such a `Mapping` or `dataclass`.

    If the input `obj` is both a `Mapping` and a `dataclass`,
    it will be serialized as a `Mapping`.

    Example:
    ```python
    data = {
        "name": "John Doe",
        "age": 50,
        "children": ["Jane", "Jimmy"],
    }
    sled_output = to_sled(data)
    ```

    Sled output:
    ```sled
    name = "John Doe"
    age = 50
    children = [
      Jane
      Jimmy
    ]
    ```
    """

    serializer = SledSerializer(
        indent=indent,
        use_top_level_braces=use_top_level_braces,
        line_separator=line_separator,
        # string
        always_quote=always_quote,
        break_on_line_separator=break_on_line_separator,
        ascii_only=ascii_only,
        quote_mark=quote_mark,
        # hex
        hex_upper_case=hex_upper_case,
        hex_horizontal_separator=hex_horizontal_separator,
        hex_bytes_per_separator=hex_bytes_per_separator,
        hex_line_length=hex_line_length,
        # float
        decimal_mark=decimal_mark,
        exponent_prefix=exponent_prefix,
        use_thousands_separator=use_thousands_separator,
    )
    return serializer.to_sled(obj)


class SledSerializer(SledSerializerBasic):
    """
    Converts Python objects to Sled.

    Example:
    ```python
    data = {
        "name": "John Doe",
        "age": 50,
        "children": ["Jane", "Jimmy"],
    }
    sled_serializer = SledSerializer()
    sled_output = sled_serializer.to_sled(data)
    ```

    Sled output:
    ```sled
    name = "John Doe"
    age = 50
    children = [
      Jane
      Jimmy
    ]
    ```
    """

    def __init__(
        self,
        *,
        indent: str = DEFAULT_INDENT,
        use_top_level_braces: bool = DEFAULT_USE_TOP_LEVEL_BRACES,
        line_separator: LineSeparator = DEFAULT_LINE_SEPARATOR,
        # strings
        always_quote: bool = DEFAULT_ALWAYS_QUOTE,
        ascii_only: bool = DEFAULT_ASCII_ONLY,
        break_on_line_separator: bool = DEFAULT_BREAK_ON_LINE_SEPARATOR,
        quote_mark: QuoteMarkType = DEFAULT_QUOTE_MARK,
        # `hex`
        hex_upper_case: bool = DEFAULT_HEX_UPPER_CASE,
        hex_horizontal_separator: HexHorizontalSeparator = DEFAULT_HEX_HORIZONTAL_SEPARATOR,
        hex_bytes_per_separator: int = DEFAULT_HEX_BYTES_PER_SEPARATOR,
        hex_line_length: int = DEFAULT_HEX_LINE_LENGTH,
        # `float`
        decimal_mark: DecimalMarkType = DEFAULT_DECIMAL_MARK,
        exponent_prefix: ExponentPrefixType = DEFAULT_EXPONENT_PREFIX,
        use_thousands_separator: bool = DEFAULT_USE_THOUSANDS_SEPARATOR,
    ) -> None:
        """
        Args:
            indent:
                The incremental indent added for each layer of nesting.
                Can only contain spaces and tabs.
            use_top_level_braces:
                If `True`, encloses the top level key-value pairs in
                an outermost pair of curly braces, like a `map`
                (i.e. the Sled document as a whole is a Sled `map`).
                Otherwise, the top level key-value pairs are left unenclosed.
            line_separator:
                The `str` with which to separate adjacent lines.
            always_quote:
                If `True`, always serialize each `str` as a `quote`
                (never `identity`, even where the content of a `str`
                is such that it could be serialized as an `identity`).
                Otherwise, serialize as an `identity` where possible.
                Does NOT apply to segments inside any `concat` emitted;
                each segment within the `concat` must always be a `quote`.
                NOTE: If `break_on_line_separator`, each `str` containing the
                `line_separator` will be serialized as a `concat`.
            ascii_only:
                If `True`, escape all non-ASCII symbols in each `str`, so that
                the serialization output contains only ASCII characters.
                Otherwise, escape only disallowed characters.
            break_on_line_separator:
                If `True`, each `str` containing the `line_separator` will be
                serialized as a `concat`, with segments based on each
                occurrence of the `line_separator`.
                Otherwise, never use `concat`.
            quote_mark:
                Symbol with which to enclose each `quote`.
            hex_upper_case:
                If `True`, the hexadecimal letters 'A' thru 'F' will be
                in upper case. Otherwise, they will be in lower case.
            hex_horizontal_separator:
                Character (if any) with which to separate adjacent groups of
                hexadecimal characters.
            hex_bytes_per_separator:
                Defines the length of each group of hexadecimal characters
                by the number of bytes that they represent.
                Two hexadecimal characters represent a byte, so the number of
                hexadecimal characters per group is twice this number.
                Positive values count from the right, negative from the left.
                If `0`, hexadecimal characters will not be grouped.
            hex_line_length:
                Max number of characters per line in `hex` content,
                excluding any indentation.
                If `0`, `hex` content will not be split into multiple lines.
            decimal_mark:
                Symbol to use for separating the integer part and
                fractional part of each `float`.
                Can be either the period (`.`) or the comma (`,`).
            exponent_prefix:
                Character with which to prefix the exponent (if any)
                in each `float`. Can be either upper (`E`) or lower (`e`) case.
            use_thousands_separator:
                If `True`, separate digits into thousands (groups of 3) using
                the underscore (`_`).
                Otherwise, don't separate digits into groups.
        """

        super().__init__(
            indent=indent,
            use_top_level_braces=use_top_level_braces,
            line_separator=line_separator,
            # string
            always_quote=always_quote,
            ascii_only=ascii_only,
            quote_mark=quote_mark,
            # hex
            hex_upper_case=hex_upper_case,
            # float
            decimal_mark=decimal_mark,
            exponent_prefix=exponent_prefix,
        )

        # strings
        self._break_on_line_separator = break_on_line_separator

        # `hex`
        self._hex_horizontal_separator: HexHorizontalSeparator = (
            ""
            if hex_bytes_per_separator == 0
            else hex_horizontal_separator
        )
        self._hex_bytes_per_separator = (
            0
            if hex_horizontal_separator == ""
            else hex_bytes_per_separator
        )
        if hex_line_length < (
            abs(self._hex_bytes_per_separator) * HEX_DIGITS_PER_BYTE
        ):
            raise ValueError(
                f"hex_line_length must be at least {HEX_DIGITS_PER_BYTE}x "
                "the absolute value of hex_bytes_per_separator, "
                f"but it is only {hex_line_length}, which is less than "
                f"{abs(self._hex_horizontal_separator) * HEX_DIGITS_PER_BYTE}"
            )
        self._hex_line_length = hex_line_length

        # `float`
        self._use_thousands_separator = use_thousands_separator

    def to_hex(self, b: bytes, indent: str) -> str:
        content = self._to_hex_content(b)

        if (
            self._hex_line_length <= 0
            or len(content) < self._hex_line_length
        ):
            return (
                f"{KEYWORD_MARK}{HEX_KEYWORD_NAME}"
                f"{HEX_OPEN_MARK}{content}{HEX_CLOSE_MARK}"
            )

        # Fold into lines
        lines = self._fold_hex_lines(
            content, self._hex_bytes_per_separator
        )
        last_line_separator = f"{self._line_separator}{indent}"
        line_separator = f"{last_line_separator}{self._indent}"
        joined_lines = "".join(f"{line_separator}{line}" for line in lines)
        return (
            f"{KEYWORD_MARK}{HEX_KEYWORD_NAME}{HEX_OPEN_MARK}"
            f"{joined_lines}{last_line_separator}{HEX_CLOSE_MARK}"
        )

    def _to_hex_content(self, b: bytes) -> str:
        content = b.hex(
            self._hex_horizontal_separator, self._hex_bytes_per_separator
        )
        return content.upper if self._hex_upper_case else content

    def _fold_hex_lines(
        self, hex_content: str, hex_bytes_per_separator: int
    ) -> List[str]:
        # If grouping from right to left, split into lines in reverse
        if hex_bytes_per_separator > 0:
            reversed_lines = self._fold_hex_lines(
                hex_content[::-1], -hex_bytes_per_separator
            )
            lines = [line[::-1] for line in reversed(reversed_lines)]

            if len(lines) > 1:
                # Pad leading line, which may be only partially filled,
                # right-aligning with subsequent lines
                lines[0] = lines[0].rjust(len(lines[1]), " ")
            return lines

        line_length = self._hex_line_length
        line_length_in_content = line_length
        if (
            hex_bytes_per_separator != 0
            and self._hex_horizontal_separator != ""
        ):
            # Keep groups intact when splitting lines,
            # and omit horizontal separator between groups on separate lines
            separator_length = len(self._hex_horizontal_separator)
            remainder_length = (self._hex_line_length + separator_length) % (
                HEX_DIGITS_PER_BYTE * hex_bytes_per_separator
                + separator_length
            )
            line_length = self._hex_line_length - remainder_length
            line_length_in_content = line_length + separator_length

        hex_content_len = len(hex_content)
        line_start_index = 0
        lines: List[str] = []
        while line_start_index < hex_content_len:
            lines.append(
                hex_content[line_start_index:line_start_index+line_length]
            )
            line_start_index += line_length_in_content
        return lines

    def to_integer(self, n: int) -> str:
        self.validate_integer(n)
        return f"{n:_d}"

    def to_float(self, x: float) -> str:
        return self.to_float_custom(x, self._use_thousands_separator)

    def to_string(self, s: str, indent: str) -> str:
        if s == "":
            # quote (identity cannot be empty)
            return self._quote_mark * 2

        identity = self._try_to_identity(s)
        if identity != "":
            return identity

        content = self.escape_string(s)

        if not self._break_on_line_separator:
            return f"{self._quote_mark}{content}{self._quote_mark}"

        lines_wo_separator = content.split(self._line_separator_escape)
        if len(lines_wo_separator) == 1:
            return f"{self._quote_mark}{content}{self._quote_mark}"

        # Break on line separator
        lines = [
            f"{line}{self._line_separator_escape}"
            for line in lines_wo_separator
        ]
        lines[-1] = lines_wo_separator[-1]
        last_line_separator = f"{self._line_separator}{indent}"
        segment_separator = f"{last_line_separator}{self._indent}"
        segments_str = "".join(
            f"{segment_separator}{self._quote_mark}{line}{self._quote_mark}"
            for line in lines
        )
        return (
            f"{KEYWORD_MARK}{CONCAT_KEYWORD_NAME}{CONCAT_OPEN_MARK}"
            f"{segments_str}{last_line_separator}{CONCAT_CLOSE_MARK}"
        )
