from pathlib import Path
from typing import Dict, List

import pytest

import parsled


class TestIntegerValue:
    @pytest.fixture(scope="class")
    def arbitrary_key(self) -> str:
        return "data"

    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("integer-basic.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()
    
    @pytest.fixture(scope="class")
    def expected_dict(self, arbitrary_key: str) -> Dict[str, List[int]]:
        return {arbitrary_key: [0, 0, 0, -1, 1, 1]}

    def test_parser(
        self,
        sled_text: str,
        expected_dict: Dict[str, List[int]],
        arbitrary_key: str,
    ) -> None:
        actual_dict = parsled.from_sled(sled_text)
        assert expected_dict == actual_dict
        actual_list = actual_dict[arbitrary_key]
        for actual in actual_list:
            assert isinstance(actual, int)
