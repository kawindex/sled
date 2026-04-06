from pathlib import Path
from typing import Dict

import pytest

import parsled


class TestIntegerRangeKey:
    @pytest.fixture(scope="class")
    def integer_range_data_dir(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("integer-range-key")

    @pytest.fixture(
        scope="class",
        params=("overflow-negative.sd", "overflow-positive.sd"),
    )
    def overflow_sled_path(
        self, request: pytest.FixtureRequest, integer_range_data_dir: Path
    ) -> Path:
        return integer_range_data_dir.joinpath(request.param)

    @pytest.fixture(scope="class")
    def overflow_sled_text(self, overflow_sled_path: Path) -> str:
        return overflow_sled_path.read_text().strip()

    def test_overflow(self, overflow_sled_text: str) -> None:
        with pytest.raises(parsled.SledError) as excinfo:
            parsled.from_sled(overflow_sled_text)
        assert parsled.SledErrorCategory.NUMBER_RANGE == excinfo.value.error_category

    @pytest.fixture(scope="class")
    def control_sled_path(self, integer_range_data_dir: Path) -> Path:
        return integer_range_data_dir.joinpath("control.sd")

    @pytest.fixture(scope="class")
    def control_sled_text(self, control_sled_path: Path) -> str:
        return control_sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def control_expected_dict(self) -> Dict[str, Dict[int, str]]:
        return {
            "basic": {
                9223372036854775807: "positive_int",
                -9223372036854775808: "negative_int",
                0: "positive_long",
            },
            "underscore": {
                9223372036854775807: "positive_int_with_underscore",
                -9223372036854775808: "negative_int_with_underscore",
                0: "negative_long",
            },
            "long": {
                9223372036854775807: "positive_int_with_long",
                -9223372036854775808: "negative_int_with_long",
            },
        }

    def test_control_parse(
        self,
        control_sled_text: str,
        control_expected_dict: Dict[str, Dict[int, str]],
    ) -> None:
        actual_data = parsled.from_sled(control_sled_text)
        assert control_expected_dict == actual_data

    def test_control_round_trip(
        self, control_expected_dict: Dict[str, Dict[int, str]]
    ) -> None:
        sled_text = parsled.to_sled(control_expected_dict)
        round_trip_data = parsled.from_sled(sled_text)
        assert control_expected_dict == round_trip_data

    def test_control_round_trip_mini(
        self, control_expected_dict: Dict[str, Dict[int, str]]
    ) -> None:
        sled_text = parsled.to_sled_mini(control_expected_dict)
        round_trip_data = parsled.from_sled(sled_text)
        assert control_expected_dict == round_trip_data

    def test_control_round_trip_serializer(
        self,
        each_sled_serializer,
        control_expected_dict: Dict[str, Dict[int, str]],
    ) -> None:
        sled_text = each_sled_serializer.to_sled(control_expected_dict)
        round_trip_data = parsled.from_sled(sled_text)
        assert control_expected_dict == round_trip_data


class TestIntegerRangeValue:
    @pytest.fixture(scope="class")
    def integer_range_data_dir(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("integer-range-value")

    @pytest.fixture(
        scope="class",
        params=("overflow-negative.sd", "overflow-positive.sd"),
    )
    def overflow_sled_path(
        self, request: pytest.FixtureRequest, integer_range_data_dir: Path
    ) -> Path:
        return integer_range_data_dir.joinpath(request.param)

    @pytest.fixture(scope="class")
    def overflow_sled_text(self, overflow_sled_path: Path) -> str:
        return overflow_sled_path.read_text().strip()

    def test_overflow(self, overflow_sled_text: str) -> None:
        with pytest.raises(parsled.SledError) as excinfo:
            parsled.from_sled(overflow_sled_text)
        assert parsled.SledErrorCategory.NUMBER_RANGE == excinfo.value.error_category

    @pytest.fixture(scope="class")
    def control_sled_path(self, integer_range_data_dir: Path) -> Path:
        return integer_range_data_dir.joinpath("control.sd")

    @pytest.fixture(scope="class")
    def control_sled_text(self, control_sled_path: Path) -> str:
        return control_sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def control_expected_data(self) -> Dict[str, int]:
        return {
            "positive_int": 9223372036854775807,
            "negative_int": -9223372036854775808,
            "positive_long": 0,
            "negative_long": 0,
            "positive_int_with_long": 9223372036854775807,
            "negative_int_with_long": -9223372036854775808,
            "positive_int_with_underscore": 9223372036854775807,
            "negative_int_with_underscore": -9223372036854775808,
        }

    def test_control_parse(
        self,
        control_sled_text: str,
        control_expected_data: Dict[str, int],
    ) -> None:
        actual_data = parsled.from_sled(control_sled_text)
        assert control_expected_data == actual_data

    def test_control_round_trip(
        self, control_expected_data: Dict[str, int]
    ) -> None:
        sled_text = parsled.to_sled(control_expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert control_expected_data == round_trip_data

    def test_control_round_trip_mini(
        self, control_expected_data: Dict[str, int]
    ) -> None:
        sled_text = parsled.to_sled_mini(control_expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert control_expected_data == round_trip_data

    def test_control_round_trip_serializer(
        self, each_sled_serializer, control_expected_data: Dict[str, int]
    ) -> None:
        sled_text = each_sled_serializer.to_sled(control_expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert control_expected_data == round_trip_data
