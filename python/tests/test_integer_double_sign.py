from pathlib import Path
from typing import Dict

import pytest

import pysled


@pytest.fixture(scope="module")
def integer_double_sign_test_data_dir(core_test_data_dir: Path) -> Path:
    return core_test_data_dir.joinpath("integer-double-sign")


class TestIntegerDoubleSignInvalidValue:
    @pytest.fixture(scope="class", params=("pos", "neg"))
    def first_sign(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class", params=("pos", "neg"))
    def second_sign(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class", params=("0", "1"))
    def base_integer(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class")
    def sled_path(
        self,
        integer_double_sign_test_data_dir: Path,
        first_sign: str,
        second_sign: str,
        base_integer: str,
    ) -> Path:
        return integer_double_sign_test_data_dir.joinpath(
            f"invalid-value-{first_sign}-{second_sign}-{base_integer}.sd"
        )
    
    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_parse(self, sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(sled_text)
        assert pysled.SledErrorCategory.SYNTAX == excinfo.value.error_category


class TestIntegerDoubleSignValidValue:
    @pytest.fixture(scope="class")
    def sled_path(self, integer_double_sign_test_data_dir: Path) -> Path:
        return integer_double_sign_test_data_dir.joinpath("valid-value.sd")
    
    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, int]:
        return {
            "pos": 1,
            "eq": 0,
            "neg": -1,
        }

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, int]
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data


class TestIntegerDoubleSignInvalidKey:
    @pytest.fixture(scope="class", params=("pos", "neg"))
    def first_sign(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class", params=("pos", "neg"))
    def second_sign(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class", params=("0", "1"))
    def base_integer(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class")
    def sled_path(
        self,
        integer_double_sign_test_data_dir: Path,
        first_sign: str,
        second_sign: str,
        base_integer: str,
    ) -> Path:
        return integer_double_sign_test_data_dir.joinpath(
            f"invalid-key-{first_sign}-{second_sign}-{base_integer}.sd"
        )
    
    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_parse(self, sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(sled_text)
        assert pysled.SledErrorCategory.SYNTAX == excinfo.value.error_category


class TestIntegerDoubleSignValidKey:
    @pytest.fixture(scope="class")
    def sled_path(self, integer_double_sign_test_data_dir: Path) -> Path:
        return integer_double_sign_test_data_dir.joinpath("valid-key.sd")
    
    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, Dict[int, str]]:
        return {
            "data": {
                1: "pos",
                0: "eq",
                -1: "neg",
            }
        }

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, Dict[int, str]]
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data
