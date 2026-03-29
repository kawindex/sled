import math
from pathlib import Path
from typing import Dict, List

import pytest

import pysled


class TestFloatNormal:
    @pytest.fixture(scope="class")
    def arbitrary_key(self) -> str:
        return "data"

    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("float-normal.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def float_values(self) -> List[float]:
        return [
            789.0,
            271.0,
            0.987_654,
            0.123,
            -456.0,
            0.01234567,
            6870.0,
            4.56e8,
            321.0,
            275.0,
            0.54_30e2,
            12.30456,
            -3.14e6,
            628e2,
            -0.00123,
            1.23e6,
            -456.0,
        ]

    @pytest.fixture(scope="class")
    def expected_dict(
        self, float_values: List[float], arbitrary_key: str
    ) -> Dict[str, List[float]]:
        approx_list = [pytest.approx(expected) for expected in float_values]
        return {arbitrary_key: approx_list}

    @pytest.fixture(scope="class")
    def input_dict(
        self, float_values: List[float], arbitrary_key: str
    ) -> Dict[str, List[float]]:
        return {arbitrary_key: float_values}

    def test_parser(
        self,
        sled_text: str,
        expected_dict: Dict[str, List[float]],
        arbitrary_key: str,
    ) -> None:
        actual_dict = pysled.from_sled(sled_text)
        assert expected_dict == actual_dict
        actual_list = actual_dict[arbitrary_key]
        for actual in actual_list:
            assert isinstance(actual, float)

    def test_round_trip(
        self,
        input_dict: Dict[str, List[float]],
        expected_dict: Dict[str, List[float]],
        arbitrary_key: str,
    ) -> None:
        sled_text = pysled.to_sled(input_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert expected_dict == round_trip_dict
        round_trip_list = round_trip_dict[arbitrary_key]
        for actual in round_trip_list:
            assert isinstance(actual, float)

    def test_round_trip_mini(
        self,
        input_dict: Dict[str, List[float]],
        expected_dict: Dict[str, List[float]],
        arbitrary_key: str,
    ) -> None:
        sled_text = pysled.to_sled_mini(input_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert expected_dict == round_trip_dict
        round_trip_list = round_trip_dict[arbitrary_key]
        for actual in round_trip_list:
            assert isinstance(actual, float)

    def test_round_trip_serializer(
        self,
        each_sled_serializer,
        input_dict: Dict[str, List[float]],
        expected_dict: Dict[str, List[float]],
        arbitrary_key: str,
    ) -> None:
        sled_text = each_sled_serializer.to_sled(input_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert expected_dict == round_trip_dict
        round_trip_list = round_trip_dict[arbitrary_key]
        for actual in round_trip_list:
            assert isinstance(actual, float)
