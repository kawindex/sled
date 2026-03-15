from pathlib import Path
from typing import Dict

import pytest

import pysled


class TestHexLorem:
    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("hex-lorem.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def lorem_ipsum(self) -> bytes:
        return (
            b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do '
            b'eiusmod tempor incididunt ut labore et dolore magna aliqua. '
            b'Ut enim ad minim veniam, quis nostrud exercitation ullamco '
            b'laboris nisi ut aliquip ex ea commodo consequat. Duis aute '
            b'irure dolor in reprehenderit in voluptate velit esse cillum '
            b'dolore eu fugiat nulla pariatur. Excepteur sint occaecat '
            b'cupidatat non proident, sunt in culpa qui officia deserunt '
            b'mollit anim id est laborum.'
        )

    @pytest.fixture(scope="class")
    def expected_data(self, lorem_ipsum: bytes) -> Dict[str, pysled.Entity]:
        by_separator = {
            "nothing": lorem_ipsum,
            "underscore": lorem_ipsum,
            "space": lorem_ipsum,
            "tab": lorem_ipsum,
        }
        return {
            "UPPER": by_separator,
            "lower": by_separator,
            "mix": lorem_ipsum,
        }

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data
