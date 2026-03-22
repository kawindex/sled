import math
from pathlib import Path
from typing import Dict

import pytest

import pysled


@pytest.fixture(scope="module")
def float_keyword_test_data_dir(core_test_data_dir: Path) -> Path:
    return core_test_data_dir.joinpath("float-keyword")

class TestFloatKeywordInvalid:
    @pytest.fixture(scope="class", params=("neg", "pos"))
    def sign(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class", params=("sign", "keyword"))
    def invalid_component(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class", params=("inf", "ninf", "nan"))
    def base_keyword(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class")
    def sled_path(
        self,
        invalid_component: str,
        sign: str,
        base_keyword: str,
        float_keyword_test_data_dir: Path,
    ) -> Path:
        return float_keyword_test_data_dir.joinpath(
            f"invalid-{invalid_component}-{sign}-{base_keyword}.sd"
        )

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_parse_invalid(self, sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(sled_text)
        assert pysled.SledErrorCategory.SYNTAX == excinfo.value.error_category


class TestFloatKeywordValid:
    @pytest.fixture(scope="class")
    def sled_path(self, float_keyword_test_data_dir: Path) -> str:
        return float_keyword_test_data_dir.joinpath("valid.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_valid(self, sled_text: str) -> None:
        d = pysled.from_sled(sled_text)
        check_float_keyword_valid(d)
        round_trip_sled_text = pysled.to_sled(d)
        round_trip_data = pysled.from_sled(round_trip_sled_text)
        check_float_keyword_valid(round_trip_data)


def check_float_keyword_valid(d: Dict[str, pysled.Entity]) -> None:
    assert 11 == len(d)

    for k in ("inf", "@inf", "x"):
        v = d[k]
        assert isinstance(v, float)
        assert math.isinf(v)
        assert v > 0

    for k in ("ninf", "@ninf", "y"):
        v = d[k]
        assert isinstance(v, float)
        assert math.isinf(v)
        assert v < 0

    for k in ("nan", "@nan", "z"):
        v = d[k]
        assert isinstance(v, float)
        assert math.isnan(v)

    pi = d["pi"]
    assert isinstance(pi, float)
    assert math.isclose(3.14159, pi)

    neg_pi = d["-pi"]
    assert isinstance(neg_pi, float)
    assert math.isclose(-3.14, neg_pi)
