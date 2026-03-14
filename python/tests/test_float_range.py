import math
import sys
from pathlib import Path
from typing import Dict

import pytest

import pysled


@pytest.fixture(scope="module")
def assert_sys_float_max() -> None:
    assert pytest.approx(1.7976931348623e308) == sys.float_info.max, (
        "these tests should run on a system with the appropriate max float"
    )


def test_sys_float_range(assert_sys_float_max: None) -> None:
    pass


@pytest.fixture(scope="module")
def float_range_test_data_dir(core_test_data_dir: Path) -> Path:
    return core_test_data_dir.joinpath("float-range")


class TestFloatOutOfRange:
    @pytest.fixture(scope="class", params=("overflow", "underflow"))
    def exceed_label(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(
        scope="class",
        params=("implicit", "positive", "negative"),
    )
    def sign_label(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class")
    def sled_path(
        self,
        float_range_test_data_dir: Path,
        exceed_label: str,
        sign_label: str,
    ) -> Path:
        sled_file_name = f"{exceed_label}-{sign_label}.sd"
        return float_range_test_data_dir.joinpath(sled_file_name)

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_parse(self, sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(sled_text)
        assert pysled.SledErrorCategory.NUMBER_RANGE == excinfo.value.error_category


class TestLargeFloat:
    @pytest.fixture(scope="class")
    def sled_path(self, float_range_test_data_dir: Path) -> Path:
        return float_range_test_data_dir.joinpath("large.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[
        str, Dict[str, Dict[str, Dict[str, float]]]
    ]:
        by_sign = {
            "implicit-positive": pytest.approx(1.797693e308),
            "explicit-positive": pytest.approx(1.797693e308),
            "negative": pytest.approx(-1.797693e308),
        }
        by_exp_sign = {
            "implicit-exp-sign": by_sign,
            "explicit-exp-sign": by_sign,
        }
        by_exp_case = {
            "upper-case-exp": by_exp_sign,
            "lower-case-exp": by_exp_sign,
        }
        by_decimal_mark = {
            "dot": by_exp_case,
            "comma": by_exp_case,
        }
        return by_decimal_mark

    def test_parse(
        self,
        sled_text: str,
        expected_data: Dict[str, Dict[str, Dict[str, Dict[str, float]]]],
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data
        for by_exp_case in actual_data.values():
            for by_exp_sign in by_exp_case.values():
                for by_sign in by_exp_sign.values():
                    for actual in by_sign.values():
                        assert isinstance(actual, float)
                        assert math.isfinite(actual)


class TestSmallFloat:
    @pytest.fixture(scope="class")
    def sled_path(self, float_range_test_data_dir: Path) -> Path:
        return float_range_test_data_dir.joinpath("small.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()
    
    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[
        str, Dict[str, Dict[str, Dict[str, float]]]
    ]:
        positive_values = {
            "near-zero": pytest.approx(4.95e-324, abs=sys.float_info.min),
            "subnormal": pytest.approx(2.225e-308, rel=1e-3, abs=0),
            "normal": pytest.approx(2.226e-308, rel=1e-3, abs=0),
        }
        by_sign = {
            "implicit-positive": positive_values,
            "explicit-positive": positive_values,
            "negative": {
                "near-zero": pytest.approx(-4.95e-324, abs=sys.float_info.min),
                "subnormal": pytest.approx(-2.225e-308, rel=1e-3, abs=0),
                "normal": pytest.approx(-2.226e-308, rel=1e-3, abs=0),
            }
        }
        by_exp_case = {
            "lower-case-exp": by_sign,
            "upper-case-exp": by_sign,
        }
        by_decimal_mark = {
            "dot": by_exp_case,
            "comma": by_exp_case,
        }
        return by_decimal_mark
    
    def test_parse(
        self,
        sled_text: str,
        expected_data: Dict[str, Dict[str, Dict[str, Dict[str, float]]]],
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data
        for by_exp_case in actual_data.values():
            for by_sign in by_exp_case.values():
                for values in by_sign.values():
                    for actual in values.values():
                        assert isinstance(actual, float)
                        assert math.isfinite(actual)
