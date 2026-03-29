from pathlib import Path
from typing import Dict

import pytest

import pysled


class TestKeywordGeneral:
    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("keyword-general.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, pysled.Entity]:
        return {
            "nil": None,
            "true": True,
            "false": False,
            "hex": b'',
            "concat": "",

            "@nil": None,
            "@true": True,
            "@false": False,
            "@hex": b'',
            "@hex()": b'',
            "@hex( )": b'',
            "@concat": "",
            "@concat()": "",
            "@concat(   )": "",

            "@@nil": [None, "hello world", True, False, None, "false"],
            "@@true": {"true": False},
            "@@false": {"false": True},
            "@@nan": {
                "pi": 3.14,
                "nan": True,
                "true": None,
                "nil": False,
            },
            "@@inf": None,
            "@@ninf": {"inf": "@inf", "@ninf": "ninf", "ninf": True},
        }

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data

    def test_round_trip(
        self, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        sled_text = pysled.to_sled(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_mini(
        self, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        sled_text = pysled.to_sled_mini(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer(
        self, each_sled_serializer, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        sled_text = each_sled_serializer.to_sled(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data
