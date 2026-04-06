"""
Tests based on JSON benchmark data from:
- https://github.com/miloyip/nativejson-benchmark
- https://github.com/mattgiles/mujson
"""

import json
from pathlib import Path
from typing import Dict

import pytest

import parsled


class TestLarge:
    @pytest.fixture(scope="class")
    def large_test_data_dir(self, sled_test_data_dir: Path) -> Path:
        return sled_test_data_dir.joinpath("large")

    @pytest.fixture(
        scope="class",
        params=(
            "apache",
            "canada",
            "citm",
            "github",
            "instruments",
            "mesh",
            "tweet",
            "twitter",
        ),
    )
    def large_test_data_file_stem(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class")
    def json_data(
        self, large_test_data_dir: Path, large_test_data_file_stem: str
    ) -> Dict[str, object]:
        json_file_name = f"{large_test_data_file_stem}.json"
        test_data_file_path = large_test_data_dir.joinpath(json_file_name)
        with test_data_file_path.open(mode="r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture(
        scope="class",
        params=(".sd", "-mini.sd", "-ascii.sd"),
    )
    def sled_file_name(
        self, request: pytest.FixtureRequest, large_test_data_file_stem: str
    ) -> str:
        return f"{large_test_data_file_stem}{request.param}"

    @pytest.fixture(scope="class")
    def sled_text(self, large_test_data_dir: Path, sled_file_name: str) -> str:
        test_data_file_path = large_test_data_dir.joinpath(sled_file_name)
        return test_data_file_path.read_text(encoding="utf-8")

    def test_parse(self, sled_text: str, json_data: dict) -> None:
        actual_data = parsled.from_sled(sled_text)
        assert json_data == actual_data

    def test_round_trip(self, json_data: dict) -> None:
        sled_text = parsled.to_sled(json_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert json_data == round_trip_data

    def test_round_trip_mini(self, json_data: dict) -> None:
        sled_text = parsled.to_sled_mini(json_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert json_data == round_trip_data

    def test_round_trip_serializer(
        self, each_sled_serializer, json_data: dict
    ) -> None:
        sled_text = each_sled_serializer.to_sled(json_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert json_data == round_trip_data
