from types import MappingProxyType
from typing import Any, Mapping, NamedTuple

import pytest

from parsled._serializer import HexHorizontalSeparator


class HexLength(NamedTuple):
    hex_bytes_per_separator: int
    hex_line_length: int


@pytest.fixture(scope="package")
def sled_serializer_kwargs_hex(
    _ser_arg_hex_upper_case: bool,
    _ser_arg_hex_horizontal_separator: HexHorizontalSeparator,
    _ser_args_hex_length: HexLength,
) -> Mapping[str, Any]:
    d = {
        "hex_upper_case": _ser_arg_hex_upper_case,
        "hex_horizontal_separator": _ser_arg_hex_horizontal_separator,
        "hex_bytes_per_separator": _ser_args_hex_length.hex_bytes_per_separator,
        "hex_line_length": _ser_args_hex_length.hex_line_length,
    }
    return MappingProxyType(d)


@pytest.fixture(scope="package", params=(True, False))
def _ser_arg_hex_upper_case(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(scope="package", params=HexHorizontalSeparator.__args__)
def _ser_arg_hex_horizontal_separator(
    request: pytest.FixtureRequest
) -> HexHorizontalSeparator:
    return request.param


@pytest.fixture(
    scope="package",
    params=(
        HexLength(-16, 0), HexLength(-16, 32), HexLength(-16, 100),
        HexLength(-5, 0), HexLength(-5, 20), HexLength(-5, 64), HexLength(-5, 100),
        HexLength(-4, 0), HexLength(-4, 10), HexLength(-4, 64), HexLength(-4, 100),
        HexLength(-2, 0), HexLength(-2, 20), HexLength(-2, 64), HexLength(-2, 100),
        HexLength(-1, 0), HexLength(-1, 20), HexLength(-1, 64), HexLength(-1, 100),
        HexLength(2, 0), HexLength(2, 10), HexLength(2, 64), HexLength(2, 100),
        HexLength(3, 0), HexLength(3, 20), HexLength(3, 64), HexLength(3, 100),
        HexLength(8, 0), HexLength(8, 16), HexLength(8, 20), HexLength(8, 64), HexLength(8, 100),
        HexLength(10, 0), HexLength(10, 20), HexLength(10, 64), HexLength(10, 100),
    ),
)
def _ser_args_hex_length(request: pytest.FixtureRequest) -> HexLength:
    return request.param
