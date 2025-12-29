"""
`SledSerializerBasic` is intended to serve as a base class for serializers,
but should also work on its own.
"""

import dataclasses
import inspect
import math
from collections import Counter
from collections.abc import Hashable, Iterable
from typing import Any, Mapping, Optional, TypeVar

from pysled._keyword_literal import KeywordLiteral
from pysled._sled_error import SledError, SledErrorCategory
from pysled.spec import (
    C0_CONTROL_SET,
    C0_SIMPLE_ESCAPE_SET,
    DEFAULT_DECIMAL_MARK,
    DEFAULT_EXPONENT_PREFIX,
    DEFAULT_INDENT,
    DEFAULT_QUOTE_MARK,
    DEFAULT_LINE_SEPARATOR,
    IDENTITY_DISALLOWED_START_SYMBOLS,
    IDENTITY_DISALLOWED_SYMBOLS,
    ESCAPE_CHARACTER,
    ESCAPE_CHARACTER_ESCAPE,
    HEX_CLOSE_MARK,
    HEX_KEYWORD_NAME,
    HEX_OPEN_MARK,
    HORIZONTAL_SPACE_SET,
    KEY_VALUE_SEPARATOR,
    KEYWORD_MARK,
    LINE_SEPARATOR_ESCAPES,
    LIST_CLOSE_MARK,
    LIST_OPEN_MARK,
    MAP_CLOSE_MARK,
    MAP_OPEN_MARK,
    SIMPLE_ESCAPE_SEQUENCES,
    SLED_INTEGER_MIN,
    SLED_INTEGER_MAX,
    UNICODE_ESCAPE_CLOSE_MARK,
    UNICODE_ESCAPE_OPEN_SEQUENCE,
    DecimalMarkType,
    ExponentPrefixType,
    LineSeparator,
    QuoteMarkType
)


SLED_CUSTOM_SERIALIZATION_METHOD_NAME = "to_sled_serializable"
"""
Name of the method to implement for custom Sled serialization.

The method will override any default serialization. It will be called
without passing any arguments (like `obj.to_sled_serializable()`),
and its return value will then be serialized in the original object's stead.
"""

# Default settings
DEFAULT_USE_TOP_LEVEL_BRACES = False
DEFAULT_ALWAYS_QUOTE = False
DEFAULT_ASCII_ONLY = False
DEFAULT_HEX_UPPER_CASE = False

H = TypeVar("H", bound=Hashable)


class SledSerializerBasic:
    """A basic serializer for Sled."""

    def __init__(
        self,
        *,
        indent: str = DEFAULT_INDENT,
        use_top_level_braces: bool = DEFAULT_USE_TOP_LEVEL_BRACES,
        line_separator: LineSeparator = DEFAULT_LINE_SEPARATOR,
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
                Does NOT apply to segments inside any `concat` emitted.
                Each segment within the `concat` will always be a `quote`,
                regardless of the `always_quote` argument.
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

        if not HORIZONTAL_SPACE_SET.issuperset(indent):
            raise ValueError("indent can only contain spaces and tabs")
        self._indent = indent
        self._use_top_level_braces = use_top_level_braces

        # line separator
        self._line_separator = line_separator
        try:
            self._line_separator_escape = (
                LINE_SEPARATOR_ESCAPES[line_separator]
            )
        except KeyError as ke:
            ve = ValueError(f"line separator not recognized: {line_separator}")
            raise ve from ke

        # strings
        self._always_quote = always_quote
        self._ascii_only = ascii_only
        self._quote_mark = quote_mark
        try:
            self._quote_mark_escape = SIMPLE_ESCAPE_SEQUENCES[quote_mark]
        except KeyError as ke:
            ve = ValueError(f"quote mark not recognized: {quote_mark}")
            raise ve from ke

        # `hex`
        self._hex_upper_case = hex_upper_case

        # `float`
        self._decimal_mark = decimal_mark
        self._exponent_prefix = exponent_prefix

    def to_sled(self, obj: object) -> str:
        """
        Serializes the input `obj` as a (top level) Sled `document`.

        The input `obj` must be a `Mapping` or `dataclass` that does NOT have
        a `to_sled_serializable()` method, or an object with such a method
        returning such a `Mapping` or `dataclass`.

        If the input `obj` is serialized as a `Mapping`, either of the following
        must apply to all of its keys:
        1. Every key must be serialized as a Sled `string`; or
        2. Every key must be serialized as a Sled `integer`.

        If the input `obj` is both a `Mapping` and a `dataclass`,
        it will be serialized as a `Mapping`.
        """

        # Allow custom method override
        data = self._unwrap(obj)

        # Default serialization
        if isinstance(data, Mapping):
            pairs = [
                (self._unwrap(k), self._unwrap(v)) for k, v in data.items()
            ]
            if all(isinstance(k, str) for k, _ in pairs):
                return self.to_top_level_smap(data)
            else:
                key_type_names = ", ".join({type(k).__name__ for k, _ in data})
                raise TypeError(
                    "For serialization as a full (top level) Sled document, "
                    "the underlying data to be serialized must be "
                    "a Mapping with str keys or a dataclass, "
                    "but got a Mapping with the following key types: "
                    f"{key_type_names}"
                )
        elif (
            dataclasses.is_dataclass(data)
            and not isinstance(data, type)
        ):
            return self.to_top_level_smap(dataclasses.asdict(data))

        # Invalid underlying data
        raise TypeError(
            f"Unable to serialize {type(data).__name__} as a Sled document. "
            "For serialization as a full (top level) Sled document, "
            "the underlying data to be serialized must be "
            "a Mapping with str keys or a dataclass, "
            f"but the input {type(obj).__name__} ({repr(obj)}) "
            "involves serializing an instance of "
            f"{type(data).__name__} ({repr(data)})"
        )

    def to_top_level_smap(self, mapping: Mapping[str, Any]) -> str:
        return self.to_top_level_smap_str(mapping) + "\n"

    def to_top_level_smap_str(self, mapping: Mapping[str, Any]) -> str:
        if self._use_top_level_braces:
            content = self.to_smap_content(mapping, self._indent)
            return self._enclose_map_content(content, indent="")
        else:
            return self.to_smap_content(mapping, indent="")

    def to_entity(self, obj: object, indent: str) -> str:
        """
        Serializes the input `obj` as a Sled `entity`.

        The input `obj` must be an `Entity` instance,
        WITHOUT a `to_sled_serializable()` method,
        or an object with such a method returning such an instance.
        """

        # Allow custom method override
        data = self._unwrap(obj)

        # Default serialization
        output = self._try_base_concrete(data, indent)
        if output is not None:
            return output
        elif isinstance(data, Mapping):
            return self.to_map(data, indent)
        elif isinstance(data, Iterable):
            return self.to_list(data, indent)
        elif dataclasses.is_dataclass(data) and not isinstance(data, type):
            return self.to_map(dataclasses.asdict(data))
        else:
            raise TypeError(
                "For serialization as a Sled entity, the underlying data "
                "to be serialized must be of type Entity, "
                f"but the input {type(obj).__name__} ({repr(obj)}) "
                "involves serializing an instance of "
                f"{type(data).__name__} ({repr(data)})"
            )

    def to_concrete(self, obj: object, indent: str) -> str:
        """
        Serializes the input `obj` as a Sled `concrete`.

        The input `obj` must be a `Concrete` instance,
        WITHOUT a `to_sled_serializable()` method,
        or an object with such a method returning such an instance.
        """

        # Allow custom method override
        data = self._unwrap(obj)

        # Default serialization
        output = self._try_base_concrete(data, indent)
        if output is not None:
            return output
        else:
            raise TypeError(
                "For serialization as a Sled concrete, the underlying data "
                "to be serialized must be an instance of "
                "str, bytes, float, int, bool, or None, "
                f"but the input {type(obj).__name__} ({repr(obj)}) "
                "involves serializing an instance of "
                f"{type(data).__name__} ({repr(data)})"
            )

    def _unwrap(self, obj: object) -> object:
        bound_method = getattr(
            obj, SLED_CUSTOM_SERIALIZATION_METHOD_NAME, None
        )
        if bound_method is None:
            return obj

        # Validate that it is callable
        if not callable(bound_method):
            raise TypeError(
                f"{type(obj).__name__}."
                f"{SLED_CUSTOM_SERIALIZATION_METHOD_NAME} "
                "must be callable."
            )

        # Validate that it can be called without passing in any arguments
        (
            arg_names, _, _, arg_defaults, kwonlyargs, kwonlydefaults, _
        ) = inspect.getfullargspec(bound_method)
        if not (
            len(arg_names) == len(arg_defaults)
            and set(kwonlyargs) == set(kwonlydefaults)
        ):
            raise TypeError(
                f"Must be able to call {type(obj).__name__}."
                f"{SLED_CUSTOM_SERIALIZATION_METHOD_NAME}() "
                "without passing arguments."
            )

        return self._unwrap(bound_method())

    def _try_base_concrete(self, obj: object, indent: str) -> Optional[str]:
        """
        If the input `obj` is an instance of any of the base `Concrete` types
        (`str`, `bytes`, `float`, `int`, `bool`, `None`), serializes it
        as a Sled `concrete`, with the given existing `indent`.
        Otherwise, returns `None`.
        """

        if obj is None:
            return KeywordLiteral.NIL.value.lexeme
        elif isinstance(obj, bool):
            return self.to_boolean(obj)
        elif isinstance(obj, bytes):
            return self.to_hex(obj, indent)
        elif isinstance(obj, int):
            return self.to_integer(obj)
        elif isinstance(obj, float):
            return self.to_float(obj)
        elif isinstance(obj, str):
            return self.to_string(obj, indent)
        else:
            return None

    def to_map(self, mapping: Mapping, indent: str) -> str:
        nested_indent = f"{indent}{self._indent}"
        content = self.to_map_content(mapping, nested_indent)
        return self._enclose_map_content(content, indent)

    def _enclose_map_content(self, content: str, indent: str) -> str:
        last_line_separator = f"{self._line_separator}{indent}"
        line_separator = f"{self._line_separator}{indent}{self._indent}"
        return (
            f"{MAP_OPEN_MARK}{line_separator}{content}"
            f"{last_line_separator}{MAP_CLOSE_MARK}"
        )

    def to_map_content(self, mapping: Mapping, indent: str) -> str:
        data = [(self._unwrap(k), self._unwrap(v)) for k, v in mapping.items()]
        if all(isinstance(k, str) for k, _ in data):
            self._validate_distinct_map_keys(k for k, _ in data)
            return self.to_smap_content(dict(data), indent)
        elif all(isinstance(k, int) for k, _ in data):
            self._validate_distinct_map_keys(k for k, _ in data)
            return self.to_imap_content(dict(data), indent)
        else:
            key_type_names = ", ".join({type(k).__name__ for k, _ in data})
            raise TypeError(
                f"Unable to serialize mapping as a Sled smap or imap. "
                "For smap, every key must serialize to a string. "
                "For imap, every key must serialize to an integer. "
                f"Got the following key types: {key_type_names}"
            )

    def _validate_distinct_map_keys(self, it: Iterable[H]) -> None:
        tally = Counter(it)
        dups = ", ".join(
            f"{k} ({count})" for k, count in tally.items() if count > 1
        )
        if dups:
            raise ValueError(
                "Serialization would result in repeated Sled keys "
                f"in the same map: {dups}"
            )

    def to_smap_content(self, mapping: Mapping[str, Any], indent: str) -> str:
        line_separator = f"{self._line_separator}{indent}"
        return line_separator.join(
            f"{self.to_string(k, indent)} {KEY_VALUE_SEPARATOR} "
            f"{self.to_entity(v, indent)}"
            for k, v in mapping.items()
        )

    def to_imap_content(self, mapping: Mapping[int, Any], indent: str) -> str:
        line_separator = f"{self._line_separator}{indent}"
        return line_separator.join(
            f"{self.to_integer(k)} {KEY_VALUE_SEPARATOR} "
            f"{self.to_entity(v, indent)}"
            for k, v in mapping.items()
        )

    def to_list(self, it: Iterable, indent: str) -> str:
        nested_indent = f"{indent}{self._indent}"
        last_line_separator = f"{self._line_separator}{indent}"
        line_separator = f"{self._line_separator}{nested_indent}"
        content = "".join(
            f"{line_separator}{self.to_entity(obj, nested_indent)}"
            for obj in it
        )
        return f"{LIST_OPEN_MARK}{content}{last_line_separator}{LIST_CLOSE_MARK}"

    def to_boolean(self, b: bool) -> str:
        return (
            KeywordLiteral.TRUE.value.lexeme
            if b
            else KeywordLiteral.FALSE.value.lexeme
        )

    def to_hex(self, b: bytes, indent: str) -> str:
        content = self._to_hex_content(b)
        return (
            f"{KEYWORD_MARK}{HEX_KEYWORD_NAME}"
            f"{HEX_OPEN_MARK}{content}{HEX_CLOSE_MARK}"
        )

    def _to_hex_content(self, b: bytes) -> str:
        content = b.hex()
        return content.upper if self._hex_upper_case else content

    def to_integer(self, n: int) -> str:
        self.validate_integer(n)
        return f"{n:_d}"

    def validate_integer(self, n: int) -> None:
        """Validate that the input `n` lies within the allowed range."""
        if n < SLED_INTEGER_MIN or SLED_INTEGER_MAX < n:
            reason = (
                "Value cannot be represented by a Sled integer "
                f"(overflow): {n}"
            )
            raise SledError(
                error_message=reason,
                error_category=SledErrorCategory.NUMBER_RANGE,
                reason=reason,
                start_line_num=0,
            )

    def to_float(self, x: float) -> str:
        return self.to_float_custom(x, True)

    def to_float_custom(self, x: float, use_thousands_separator: bool) -> str:
        if math.isnan(x):
            return KeywordLiteral.NAN.value.lexeme
        elif math.isinf(x):
            return (
                KeywordLiteral.NINF.value.lexeme
                if x < 0
                else KeywordLiteral.INF.value.lexeme
            )

        # Start with default decimal mark and exponent symbol
        output = f"{x:_}" if use_thousands_separator else f"{x}"

        # Adjust decimal mark
        has_decimal_mark = DEFAULT_DECIMAL_MARK in output
        if has_decimal_mark and self._decimal_mark != DEFAULT_DECIMAL_MARK:
            output = output.replace(DEFAULT_DECIMAL_MARK, self._decimal_mark)

        # Adjust exponent symbol
        has_exponent = DEFAULT_EXPONENT_PREFIX in output
        if has_exponent and self._exponent_prefix != DEFAULT_EXPONENT_PREFIX:
            output = output.replace(
                DEFAULT_EXPONENT_PREFIX, self._exponent_prefix
            )

        # If currently indistinguishable from an integer, add the decimal mark
        if not (has_decimal_mark or has_exponent):
            output = f"{output}{self._decimal_mark}0"

        return output

    def to_string(self, s: str, indent: str) -> str:
        if s == "":
            # quote (identity cannot be empty)
            return self._quote_mark * 2

        identity = self._try_to_identity(s)
        if identity != "":
            return identity

        content = self.escape_string(s)
        return f"{self._quote_mark}{content}{self._quote_mark}"

    def _try_to_identity(self, s: str) -> str:
        if (
            s == ""
            or self._always_quote
            or s[0] in IDENTITY_DISALLOWED_START_SYMBOLS
            or (not IDENTITY_DISALLOWED_SYMBOLS.isdisjoint(s))
            or any(c.isspace() for c in s)
            or (self._ascii_only and not s.isascii())
        ):
            return ""
        else:
            # identity
            return s

    def escape_string(self, s: str) -> str:
        # First escape the escape character
        content = s.replace(ESCAPE_CHARACTER, ESCAPE_CHARACTER_ESCAPE)

        # Escape the relevant quote mark
        content = content.replace(
            self._quote_mark, self._quote_mark_escape
        )

        # Escape any remaining reserved chars with special escape sequences
        for c in C0_SIMPLE_ESCAPE_SET.intersection(content):
            content = content.replace(c, SIMPLE_ESCAPE_SEQUENCES[c])

        # Escape any remaining reserved chars
        for c in C0_CONTROL_SET.intersection(content):
            content = content.replace(c, self.to_unicode_escape(c))

        # If configured, escape all other non-ASCII symbols
        if self._ascii_only:
            symbol_set = set(content)
            for c in symbol_set:
                if not c.isascii():
                    content = content.replace(c, self.to_unicode_escape(c))

        return content

    def to_unicode_escape(self, c: str) -> str:
        if len(c) != 1:
            raise ValueError(f"c must have length 1, but is {c}")
        return (
            f"{UNICODE_ESCAPE_OPEN_SEQUENCE}"
            f"{ord(c):_X}{UNICODE_ESCAPE_CLOSE_MARK}"
        )
