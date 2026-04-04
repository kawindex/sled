from pathlib import Path
from typing import Any, Dict, Mapping

import pytest

import pysled


class TestHexBasic:
    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("hex-basic.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, bytes]:
        return {
            "hexed": bytes((237,)),
            "Sled": bytes((81, 237)),
            "dEcaDE": bytes((222, 202, 222)),
            "enlarge": bytes((1, 35, 69, 103, 137, 171, 205, 239)),
            "shrink": bytes((254, 220, 186, 152, 118, 84, 50, 16)),
            "FOOSball": bytes((240, 5, 186, 17)),
            "daffodil": bytes((218, 255, 13, 17)),
            "access": bytes((172, 206, 85)),
            "FEEL": bytes((254, 225)),
            "DIABOLICAL": bytes((209, 171, 1, 28, 161)),
            "Scaffold": bytes((92, 175, 240, 29)),
            "multiple lines": bytes((
                92, 161, 171, 30,  # 5ca1ab1e
                202, 17, 171, 30,  # ca11ab1e
                171, 205, 239,  # ABcdeF
                171, 205, 239,  # abCDEf
                135, 101,  # 8765
                193, 165, 81, 192, 165, 21,  # c1A551C 0A515
                202, 254, 222, 193, 222, 29, 234, 30, 175,  # cafeDEC _1DE_1DEA 1eaf
            )),
        }

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, bytes]
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data

    def test_round_trip(self, expected_data: Dict[str, bytes]) -> None:
        sled_text = pysled.to_sled(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_with_hex_kwargs(
        self,
        expected_data: Dict[str, bytes],
        sled_serializer_kwargs_hex: Mapping[str, Any],
    ) -> None:
        sled_text = pysled.to_sled(expected_data, **sled_serializer_kwargs_hex)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_mini(self, expected_data: Dict[str, bytes]) -> None:
        sled_text = pysled.to_sled_mini(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer(
        self, each_sled_serializer, expected_data: Dict[str, bytes]
    ) -> None:
        sled_text = each_sled_serializer.to_sled(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer_with_hex_kwargs(
        self,
        expected_data: Dict[str, bytes],
        sled_serializer_kwargs_hex: Mapping[str, Any],
    ) -> None:
        serializer = pysled.SledSerializer(**sled_serializer_kwargs_hex)
        sled_text = serializer.to_sled(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data
