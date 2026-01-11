"""
Minified serialization for a more compact but less human-friendly output.

The interface is analogous to `to_sled()` and `SledSerializer` respectively.
1. Call `to_sled_mini()`.
2. Instantiate a `SledSerializerMini` and call its `to_sled()` method.

Both have the same configuration options and defaults.
Refer to their documentation for details.

Approach #1 simply does approach #2 under the hood.
Approach #2 may be useful if you want to set a configuration once
and reuse that for serialization multiple times.

```python
from pysled import SledSerializerMini, to_sled_mini

data = {}
other_data = {}

# Approach #1
sled_output = to_sled_mini(data)

# Approach #2
serializer = SledSerializerMini()
sled_output = serializer.to_sled(data)
other_sled_output = serializer.to_sled(other_data)
```
"""

from collections.abc import Iterable
from typing import Any, Mapping

from pysled._serializer_basic import (
    DEFAULT_ALWAYS_QUOTE,
    DEFAULT_ASCII_ONLY,
    DEFAULT_HEX_UPPER_CASE,
    DEFAULT_USE_TOP_LEVEL_BRACES,
    SledSerializerBasic,
)
from pysled.spec import (
    DEFAULT_DECIMAL_MARK,
    DEFAULT_EXPONENT_PREFIX,
    DEFAULT_QUOTE_MARK,
    DELIMITER_MARK,
    KEY_VALUE_SEPARATOR,
    LIST_OPEN_MARK,
    LIST_CLOSE_MARK,
    MAP_OPEN_MARK,
    MAP_CLOSE_MARK,
    DecimalMarkType,
    ExponentPrefixType,
    QuoteMarkType
)


def to_sled_mini(
    obj: object,
    *,
    use_top_level_braces: bool = DEFAULT_USE_TOP_LEVEL_BRACES,
    # string
    always_quote: bool = DEFAULT_ALWAYS_QUOTE,
    ascii_only: bool = DEFAULT_ASCII_ONLY,
    quote_mark: QuoteMarkType = DEFAULT_QUOTE_MARK,
    # hex
    hex_upper_case: bool = DEFAULT_HEX_UPPER_CASE,
    # float
    decimal_mark: DecimalMarkType = DEFAULT_DECIMAL_MARK,
    exponent_prefix: ExponentPrefixType = DEFAULT_EXPONENT_PREFIX,
) -> str:
    """
    Serializes the input `obj` as a minified (top level) Sled `document`.
    Produces a serialization output that is more compact
    but less human-friendly.

    This function has the same configuration options and defaults
    as `SledSerializerMini`.
    For details, refer to the `SledSerializerMini` documentation.

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
    sled_output = to_sled_mini(data)
    ```

    Sled output:
    ```sled
    name="John Doe";age=50;children=[Jane;Jimmy]
    ```
    """

    serializer = SledSerializerMini(
        # indent=indent,
        use_top_level_braces=use_top_level_braces,
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
    return serializer.to_sled(obj)


class SledSerializerMini(SledSerializerBasic):
    """
    Converts Python objects to minified Sled.
    Produces a serialization output that is more compact
    but less human-friendly.

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
    name="John Doe";age=50;children=[Jane;Jimmy]
    ```
    """

    EMPTY_INDENT = ""

    def __init__(
        self,
        *,
        use_top_level_braces: bool = DEFAULT_USE_TOP_LEVEL_BRACES,
        # strings
        always_quote: bool = DEFAULT_ALWAYS_QUOTE,
        ascii_only: bool = DEFAULT_ASCII_ONLY,
        quote_mark: QuoteMarkType = DEFAULT_QUOTE_MARK,
        # `hex`
        hex_upper_case: bool = DEFAULT_HEX_UPPER_CASE,
        # `float`
        decimal_mark: DecimalMarkType = DEFAULT_DECIMAL_MARK,
        exponent_prefix: ExponentPrefixType = DEFAULT_EXPONENT_PREFIX,
    ) -> None:
        """
        Args:
            use_top_level_braces:
                If `True`, encloses the top level key-value pairs in
                an outermost pair of curly braces, like a `map`
                (i.e. the Sled document as a whole is a Sled `map`).
                Otherwise, the top level key-value pairs are left unenclosed.
            always_quote:
                If `True`, always serialize each `str` as a `quote`
                (never `identity`, even where the content of a `str`
                is such that it could be serialized as an `identity`).
                Otherwise, serialize as an `identity` where possible.
            ascii_only:
                If `True`, escape all non-ASCII symbols in each `str`, so that
                the serialization output contains only ASCII characters.
                Otherwise, escape only disallowed characters.
            quote_mark:
                Symbol with which to enclose each `quote`.
            hex_upper_case:
                If `True`, the hexadecimal letters 'A' thru 'F' will be
                in upper case. Otherwise, they will be in lower case.
            decimal_mark:
                Symbol to use for separating the integer part and
                fractional part of each `float`.
                Can be either the period (`.`) or the comma (`,`).
            exponent_prefix:
                Character with which to prefix the exponent (if any)
                in each `float`. Can be either upper (`E`) or lower (`e`) case.
        """

        super().__init__(
            use_top_level_braces=use_top_level_braces,
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

    def to_top_level_smap(self, mapping: Mapping[str, Any]) -> str:
        return self.to_top_level_smap_str(mapping)

    def to_map(self, mapping: Mapping, indent: str) -> str:
        content = self.to_map_content(mapping, self.EMPTY_INDENT)
        return self._enclose_map_content(content, self.EMPTY_INDENT)

    def _enclose_map_content(self, content: str, indent: str) -> str:
        return f"{MAP_OPEN_MARK}{content}{MAP_CLOSE_MARK}"

    def to_smap_content(self, mapping: Mapping[str, Any], indent: str) -> str:
        return DELIMITER_MARK.join(
            f"{self.to_string(k, self.EMPTY_INDENT)}{KEY_VALUE_SEPARATOR}"
            f"{self.to_entity(v, self.EMPTY_INDENT)}"
            for k, v in mapping.items()
        )

    def to_imap_content(self, mapping: Mapping[str, Any], indent: str) -> str:
        return DELIMITER_MARK.join(
            f"{self.to_integer(k)}{KEY_VALUE_SEPARATOR}"
            f"{self.to_entity(v, self.EMPTY_INDENT)}"
            for k, v in mapping.items()
        )

    def to_list(self, it: Iterable, indent: str) -> str:
        content = DELIMITER_MARK.join(
            self.to_entity(obj, self.EMPTY_INDENT) for obj in it
        )
        return f"{LIST_OPEN_MARK}{content}{LIST_CLOSE_MARK}"

    def to_integer(self, n: int) -> str:
        self.validate_integer(n)
        return f"{n:d}"

    def to_float(self, x: float) -> str:
        return self.to_float_custom(x, use_thousands_separator=False) 

    def to_string(self, s: str, indent: str) -> str:
        if s == "":
            # quote (identity cannot be empty)
            return self._quote_mark * 2

        identity = self._try_to_identity(s)
        if identity != "":
            return identity

        content = self.escape_string(s)
        return f"{self._quote_mark}{content}{self._quote_mark}"
