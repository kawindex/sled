from pathlib import Path
from typing import Dict

import pytest

import pysled


class TestHexInvalid:
    @pytest.fixture(scope="class")
    def hex_invalid_data_dir(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("hex-invalid")

    @pytest.fixture(scope="class")
    def partial_byte_sled_path(self, hex_invalid_data_dir: Path) -> Path:
        return hex_invalid_data_dir.joinpath("partial-byte.sd")

    @pytest.fixture(scope="class")
    def partial_byte_sled_text(self, partial_byte_sled_path: Path) -> str:
        return partial_byte_sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def control_sled_path(self, hex_invalid_data_dir: Path) -> Path:
        return hex_invalid_data_dir.joinpath("control.sd")

    @pytest.fixture(scope="class")
    def control_sled_text(self, control_sled_path: Path) -> str:
        return control_sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, bytes]:
        return {"data": bytes((193, 165, 81, 192))}

    def test_parse_partial_byte(self, partial_byte_sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(partial_byte_sled_text)
        assert pysled.SledErrorCategory.SYNTAX == excinfo.value.error_category

    def test_parse_control(
        self, control_sled_text: str, expected_data: Dict[str, bytes]
    ) -> None:
        actual_data = pysled.from_sled(control_sled_text)
        assert expected_data == actual_data

    def test_control_round_trip(
        self, expected_data: Dict[str, bytes]
    ) -> None:
        sled_text = pysled.to_sled(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_control_round_trip_mini(
        self, expected_data: Dict[str, bytes]
    ) -> None:
        sled_text = pysled.to_sled_mini(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data
