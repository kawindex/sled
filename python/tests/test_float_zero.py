from pathlib import Path

import pytest

import parsled


class TestFloatZero:
    @pytest.fixture(scope="class")
    def arbitrary_key(self) -> str:
        return "data"

    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("float-zero.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text()

    def test_parser(self, sled_text: str, arbitrary_key: str) -> None:
        actual_dict = parsled.from_sled(sled_text)
        assert 1 == len(actual_dict)
        actual_list = actual_dict[arbitrary_key]
        for actual in actual_list:
            assert isinstance(actual, float)
            assert 0.0 == actual
