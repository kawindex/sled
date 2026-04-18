from typing import Dict, NamedTuple
import pytest

import parsled


@pytest.fixture(scope="module", params=("-", ">", " | ", "\t\\"))
def invalid_ser_arg_indent(request: pytest.FixtureRequest) -> str:
    return request.param


class HexLength(NamedTuple):
    hex_bytes_per_separator: int
    hex_line_length: int


@pytest.fixture(
    scope="module",
    params=(
        HexLength(2, -20),
        HexLength(-2, -20),
        HexLength(5, 8),
        HexLength(-5, 8),
        HexLength(8, 10),
        HexLength(-8, 10),
    ),
)
def invalid_ser_args_hex_length(request: pytest.FixtureRequest) -> HexLength:
    return request.param


class TestToSledKwargsInvalid:
    @pytest.fixture(scope="class")
    def arbitrary_data(self) -> Dict[str, parsled.Entity]:
        return {"greeting": "Hello, World!"}

    def test_invalid_indent(
        self,
        invalid_ser_arg_indent: str,
        arbitrary_data: Dict[str, parsled.Entity],
    ) -> None:
        with pytest.raises(ValueError):
            parsled.to_sled(arbitrary_data, indent=invalid_ser_arg_indent)

    def test_invalid_hex_length(
        self,
        invalid_ser_args_hex_length: HexLength,
        arbitrary_data: Dict[str, parsled.Entity],
    ) -> None:
        with pytest.raises(ValueError):
            parsled.to_sled(
                arbitrary_data,
                hex_bytes_per_separator=invalid_ser_args_hex_length.hex_bytes_per_separator,
                hex_line_length=invalid_ser_args_hex_length.hex_line_length,
            )


class TestSerializerKwargsInvalid:
    def test_invalid_indent(self, invalid_ser_arg_indent: str) -> None:
        with pytest.raises(ValueError):
            parsled.SledSerializer(indent=invalid_ser_arg_indent)

    def test_invalid_hex_length(
        self, invalid_ser_args_hex_length: HexLength
    ) -> None:
        with pytest.raises(ValueError):
            parsled.SledSerializer(
                hex_bytes_per_separator=invalid_ser_args_hex_length.hex_bytes_per_separator,
                hex_line_length=invalid_ser_args_hex_length.hex_line_length,
            )


class TestSerializerBasicKwargsInvalid:
    def test_invalid_indent(self, invalid_ser_arg_indent: str) -> None:
        with pytest.raises(ValueError):
            parsled._serializer_basic.SledSerializerBasic(
                indent=invalid_ser_arg_indent
            )
