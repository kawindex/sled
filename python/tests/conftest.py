from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import pytest

import parsled
from parsled.spec import (
    DEFAULT_INDENT,
    DecimalMarkType,
    ExponentPrefixType,
    LineSeparator,
    QuoteMarkType,
)


@pytest.fixture(scope="session")
def sled_test_data_dir() -> Path:
    return Path(__file__).parent.parent.parent.joinpath("testdata")


@pytest.fixture(scope="session")
def core_test_data_dir(sled_test_data_dir: Path) -> Path:
    return sled_test_data_dir.joinpath("core")


@pytest.fixture(
    scope="session",
    params=(
        parsled.SledSerializer,
        parsled.SledSerializerMini,
        parsled._serializer_basic.SledSerializerBasic,
    )
)
def each_sled_serializer(request: pytest.FixtureRequest):
    return request.param()


@pytest.fixture(scope="session")
def sled_serializer() -> parsled.SledSerializer:
    return parsled.SledSerializer()


@pytest.fixture(scope="session")
def sled_serializer_mini() -> parsled.SledSerializerMini:
    return parsled.SledSerializerMini()


@pytest.fixture(scope="session")
def sled_serializer_basic() -> parsled._serializer_basic.SledSerializerBasic:
    return parsled._serializer_basic.SledSerializerBasic()


@pytest.fixture(scope="session")
def sled_serializer_with_kwargs(
    sled_serializer_kwargs: Mapping[str, Any]
) -> parsled.SledSerializer:
    return parsled.SledSerializer(**sled_serializer_kwargs)


@pytest.fixture(scope="session")
def sled_serializer_mini_with_kwargs(
    sled_serializer_mini_kwargs: Mapping[str, Any]
) -> parsled.SledSerializerMini:
    return parsled.SledSerializerMini(**sled_serializer_mini_kwargs)


@pytest.fixture(scope="session")
def sled_serializer_basic_with_kwargs(
    sled_serializer_basic_kwargs: Mapping[str, Any]
) -> parsled._serializer_basic.SledSerializerBasic:
    return parsled._serializer_basic.SledSerializerBasic(
        **sled_serializer_basic_kwargs
    )


# Serializer kwargs

@pytest.fixture(scope="session")
def sled_serializer_kwargs(
    _ser_arg_indent: str,
    _ser_arg_use_top_level_braces: bool,
    _ser_arg_line_separator: LineSeparator,
    _ser_arg_always_quote: bool,
    _ser_arg_ascii_only: bool,
    _ser_arg_break_on_line_separator: bool,
    _ser_arg_quote_mark: QuoteMarkType,
    _ser_arg_decimal_mark: DecimalMarkType,
    _ser_arg_exponent_prefix: ExponentPrefixType,
    _ser_arg_use_thousands_separator: bool,
) -> Mapping[str, Any]:
    d = {
        "indent": _ser_arg_indent,
        "use_top_level_braces": _ser_arg_use_top_level_braces,
        "line_separator": _ser_arg_line_separator,
        "always_quote": _ser_arg_always_quote,
        "ascii_only": _ser_arg_ascii_only,
        "break_on_line_separator": _ser_arg_break_on_line_separator,
        "quote_mark": _ser_arg_quote_mark,
        "decimal_mark": _ser_arg_decimal_mark,
        "exponent_prefix": _ser_arg_exponent_prefix,
        "use_thousands_separator": _ser_arg_use_thousands_separator,
    }
    return MappingProxyType(d)


@pytest.fixture(scope="session")
def sled_serializer_mini_kwargs(
    _ser_arg_use_top_level_braces: bool,
    _ser_arg_always_quote: bool,
    _ser_arg_ascii_only: bool,
    _ser_arg_quote_mark: QuoteMarkType,
    _ser_arg_decimal_mark: DecimalMarkType,
    _ser_arg_exponent_prefix: ExponentPrefixType,
) -> Mapping[str, Any]:
    d = {
        "use_top_level_braces": _ser_arg_use_top_level_braces,
        "always_quote": _ser_arg_always_quote,
        "ascii_only": _ser_arg_ascii_only,
        "quote_mark": _ser_arg_quote_mark,
        "decimal_mark": _ser_arg_decimal_mark,
        "exponent_prefix": _ser_arg_exponent_prefix,
    }
    return MappingProxyType(d)


@pytest.fixture(scope="session")
def sled_serializer_basic_kwargs(
    _ser_arg_indent: str,
    _ser_arg_use_top_level_braces: bool,
    _ser_arg_line_separator: LineSeparator,
    _ser_arg_always_quote: bool,
    _ser_arg_ascii_only: bool,
    _ser_arg_quote_mark: QuoteMarkType,
    _ser_arg_decimal_mark: DecimalMarkType,
    _ser_arg_exponent_prefix: ExponentPrefixType,
) -> Mapping[str, Any]:
    d = {
        "indent": _ser_arg_indent,
        "use_top_level_braces": _ser_arg_use_top_level_braces,
        "line_separator": _ser_arg_line_separator,
        "always_quote": _ser_arg_always_quote,
        "ascii_only": _ser_arg_ascii_only,
        "quote_mark": _ser_arg_quote_mark,
        "decimal_mark": _ser_arg_decimal_mark,
        "exponent_prefix": _ser_arg_exponent_prefix,
    }
    return MappingProxyType(d)


@pytest.fixture(
    scope="session",
    params=(DEFAULT_INDENT, "\t", " \t   ", "\t\t \t\t"),
)
def _ser_arg_indent(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope="session", params=(True, False))
def _ser_arg_use_top_level_braces(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(scope="session", params=LineSeparator.__args__)
def _ser_arg_line_separator(request: pytest.FixtureRequest) -> LineSeparator:
    return request.param


@pytest.fixture(scope="session", params=(True, False))
def _ser_arg_always_quote(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(scope="session", params=(True, False))
def _ser_arg_ascii_only(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(scope="session", params=(True, False))
def _ser_arg_break_on_line_separator(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(scope="session", params=QuoteMarkType.__args__)
def _ser_arg_quote_mark(request: pytest.FixtureRequest) -> QuoteMarkType:
    return request.param


@pytest.fixture(scope="session", params=DecimalMarkType.__args__)
def _ser_arg_decimal_mark(request: pytest.FixtureRequest) -> DecimalMarkType:
    return request.param


@pytest.fixture(scope="session", params=ExponentPrefixType.__args__)
def _ser_arg_exponent_prefix(request: pytest.FixtureRequest) -> ExponentPrefixType:
    return request.param


@pytest.fixture(scope="session", params=(True, False))
def _ser_arg_use_thousands_separator(request: pytest.FixtureRequest) -> bool:
    return request.param
