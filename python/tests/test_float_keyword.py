import math
from pathlib import Path

import pytest

import pysled


class TestFloatKeyword:
    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("float-keyword.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_parse(self, sled_text: str) -> None:
        d = pysled.from_sled(sled_text)

        assert 8 == len(d)

        for k in ("nan", "@nan"):
            v = d[k]
            assert isinstance(v, float)
            assert math.isnan(v)

        for k in ("inf", "@inf"):
            v = d[k]
            assert isinstance(v, float)
            assert math.isinf(v)
            assert v > 0

        for k in ("ninf", "@ninf"):
            v = d[k]
            assert isinstance(v, float)
            assert math.isinf(v)
            assert v < 0

        pi = d["pi"]
        assert isinstance(pi, float)
        assert math.isclose(3.14159, pi)

        neg_pi = d["-pi"]
        assert isinstance(neg_pi, float)
        assert math.isclose(-3.14, neg_pi)
