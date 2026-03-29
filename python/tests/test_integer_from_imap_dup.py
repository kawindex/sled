from pathlib import Path
from typing import Dict, List

import pytest

import pysled


class TestIntegerValue:
    @pytest.fixture(scope="class")
    def arbitrary_key(self) -> str:
        return "data"

    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("integer-from-imap-dup.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_dict(self, arbitrary_key: str) -> Dict[str, List[int]]:
        expected_list = [
            123,
            123,
            124,
            8191,
            8191,
            8192,
            0,
            0,
            -1,
            2,
            2,
            3,
            -17,
            -17,
            -18,
            -20,
            -20,
            -21,
            1193,
            1193,
            1194,
            216_091,
            216_091,
            216_092,
            -364_289,
            -364_289,
            -364_290,
            705,
            705,
            704,
            1277,
            1277,
            1278,
            127_20_787,
            12_720_787,
            12_720_786,
            12_720_787,
            -1728,
            -1728,
            -1729,
            1_812_433_253,
            272_559_682,
            -399_874,
            272_559_682,
            156,
            272_559_683,
        ]
        return {arbitrary_key: expected_list}

    def test_parser(
        self,
        sled_text: str,
        expected_dict: Dict[str, List[int]],
        arbitrary_key: str
    ) -> None:
        actual_dict = pysled.from_sled(sled_text)
        assert expected_dict == actual_dict
        actual_list = actual_dict[arbitrary_key]
        for actual in actual_list:
            assert isinstance(actual, int)

    def test_round_trip(
        self, expected_dict: Dict[str, List[int]], arbitrary_key: str
    ) -> None:
        sled_text = pysled.to_sled(expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)

        assert expected_dict == round_trip_dict
        round_trip_list = round_trip_dict[arbitrary_key]
        for actual in round_trip_list:
            assert isinstance(actual, int)

    def test_round_trip_mini(
        self, expected_dict: Dict[str, List[int]], arbitrary_key: str
    ) -> None:
        sled_text = pysled.to_sled_mini(expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)

        assert expected_dict == round_trip_dict
        round_trip_list = round_trip_dict[arbitrary_key]
        for actual in round_trip_list:
            assert isinstance(actual, int)

    def test_round_trip_basic(
        self, expected_dict: Dict[str, List[int]], arbitrary_key: str
    ) -> None:
        serializer = pysled._serializer_basic.SledSerializerBasic()
        sled_text = serializer.to_sled(expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)

        assert expected_dict == round_trip_dict
        round_trip_list = round_trip_dict[arbitrary_key]
        for actual in round_trip_list:
            assert isinstance(actual, int)
