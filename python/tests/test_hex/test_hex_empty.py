from pathlib import Path
from typing import Dict

import pytest

import pysled


class TestHexEmpty:
    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("hex-empty.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, bytes]:
        return {
            "nothing": b'',
            "underscore": b'',
            "space": b'',
            "tabs": b'',
            "line": b'',
            "ws": b'',
            "mix": b'',
        }

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, bytes]
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data
