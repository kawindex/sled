import math
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

import parsled


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
        with pytest.raises(parsled.SledError) as excinfo:
            parsled.from_sled(sled_text)
        assert parsled.SledErrorCategory.NUMBER_RANGE == excinfo.value.error_category


class TestLargeFloat:
    @pytest.fixture(scope="class")
    def sled_path(self, float_range_test_data_dir: Path) -> Path:
        return float_range_test_data_dir.joinpath("large.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def data_value_positive(self) -> float:
        return 1.797693e308

    @pytest.fixture(scope="class")
    def data_value_negative(self) -> float:
        return -1.797693e308

    @pytest.fixture(scope="class")
    def expected_parse_data(
        self, data_value_positive: float, data_value_negative: float
    ) -> Dict[str, Any]:
        by_sign = {
            "implicit-positive": pytest.approx(data_value_positive),
            "explicit-positive": pytest.approx(data_value_positive),
            "negative": pytest.approx(data_value_negative),
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
        expected_parse_data: Dict[str, Any],
    ) -> None:
        actual_data = parsled.from_sled(sled_text)
        assert expected_parse_data == actual_data
        for by_exp_case in actual_data.values():
            for by_exp_sign in by_exp_case.values():
                for by_sign in by_exp_sign.values():
                    for actual in by_sign.values():
                        assert isinstance(actual, float)
                        assert math.isfinite(actual)

    @pytest.fixture(scope="class")
    def round_trip_input_data(
        self, data_value_positive: float, data_value_negative: float
    ) -> Dict[str, float]:
        return {
            "p": data_value_positive,
            "n": data_value_negative,
        }

    @pytest.fixture(scope="class")
    def round_trip_expected_data(
        self, round_trip_input_data: Dict[str, float]
    ) -> Dict[str, Any]:
        return {k: pytest.approx(v) for k, v in round_trip_input_data.items()}

    def test_round_trip(
        self,
        round_trip_input_data: Dict[str, float],
        round_trip_expected_data: Dict[str, Any],
    ) -> None:
        sled_text = parsled.to_sled(round_trip_input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert round_trip_expected_data == round_trip_data

    def test_round_trip_mini(
        self,
        round_trip_input_data: Dict[str, float],
        round_trip_expected_data: Dict[str, Any],
    ) -> None:
        sled_text = parsled.to_sled_mini(round_trip_input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert round_trip_expected_data == round_trip_data

    def test_round_trip_serializer(
        self,
        each_sled_serializer,
        round_trip_input_data: Dict[str, float],
        round_trip_expected_data: Dict[str, Any],
    ) -> None:
        sled_text = each_sled_serializer.to_sled(round_trip_input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert round_trip_expected_data == round_trip_data


class TestSmallFloat:
    @pytest.fixture(scope="class")
    def sled_path(self, float_range_test_data_dir: Path) -> Path:
        return float_range_test_data_dir.joinpath("small.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def data_value_positive_near_zero(self) -> float:
        return 4.95e-324

    @pytest.fixture(scope="class")
    def data_value_positive_subnormal(self) -> float:
        return 2.225e-308

    @pytest.fixture(scope="class")
    def data_value_positive_normal(self) -> float:
        return 2.226e-308

    @pytest.fixture(scope="class")
    def data_value_negative_near_zero(self) -> float:
        return -4.95e-324

    @pytest.fixture(scope="class")
    def data_value_negative_subnormal(self) -> float:
        return -2.225e-308

    @pytest.fixture(scope="class")
    def data_value_negative_normal(self) -> float:
        return -2.226e-308

    @pytest.fixture(scope="class")
    def data_values_positive(
        self,
        data_value_positive_near_zero: float,
        data_value_positive_subnormal: float,
        data_value_positive_normal: float,
    ) -> Dict[str, Any]:
        return {
            "near-zero": pytest.approx(
                data_value_positive_near_zero, abs=sys.float_info.min
            ),
            "subnormal": pytest.approx(
                data_value_positive_subnormal, rel=1e-3, abs=0
            ),
            "normal": pytest.approx(
                data_value_positive_normal, rel=1e-3, abs=0
            ),
        }

    @pytest.fixture(scope="class")
    def data_values_negative(
        self,
        data_value_negative_near_zero: float,
        data_value_negative_subnormal: float,
        data_value_negative_normal: float,
    ) -> Dict[str, Any]:
        return {
            "near-zero": pytest.approx(
                data_value_negative_near_zero, abs=sys.float_info.min
            ),
            "subnormal": pytest.approx(
                data_value_negative_subnormal, rel=1e-3, abs=0
            ),
            "normal": pytest.approx(
                data_value_negative_normal, rel=1e-3, abs=0
            ),
        }

    @pytest.fixture(scope="class")
    def expected_parse_data(
        self,
        data_values_positive: Dict[str, Any],
        data_values_negative: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        by_sign = {
            "implicit-positive": data_values_positive,
            "explicit-positive": data_values_positive,
            "negative": data_values_negative,
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
        expected_parse_data: Dict[str, Any],
    ) -> None:
        actual_data = parsled.from_sled(sled_text)
        assert expected_parse_data == actual_data
        for by_exp_case in actual_data.values():
            for by_sign in by_exp_case.values():
                for values in by_sign.values():
                    for actual in values.values():
                        assert isinstance(actual, float)
                        assert math.isfinite(actual)

    @pytest.fixture(scope="class")
    def round_trip_input_data(
        self,
        data_value_positive_near_zero: float,
        data_value_positive_subnormal: float,
        data_value_positive_normal: float,
        data_value_negative_near_zero: float,
        data_value_negative_subnormal: float,
        data_value_negative_normal: float,
    ) -> Dict[str, Dict[str, float]]:
        return {
            "p": {
                "near-zero": data_value_positive_near_zero,
                "subnormal": data_value_positive_subnormal,
                "normal": data_value_positive_normal,
            },
            "n": {
                "near-zero": data_value_negative_near_zero,
                "subnormal": data_value_negative_subnormal,
                "normal": data_value_negative_normal,
            }
        }

    @pytest.fixture(scope="class")
    def round_trip_expected_data(
        self,
        data_values_positive: Dict[str, Any],
        data_values_negative: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        return {
            "p": data_values_positive,
            "n": data_values_negative,
        }

    def test_round_trip(
        self,
        round_trip_input_data: Dict[str, Dict[str, float]],
        round_trip_expected_data: Dict[str, Dict[str, Any]],
    ) -> None:
        sled_text = parsled.to_sled(round_trip_input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert round_trip_expected_data == round_trip_data

    def test_round_trip_mini(
        self,
        round_trip_input_data: Dict[str, Dict[str, float]],
        round_trip_expected_data: Dict[str, Dict[str, Any]],
    ) -> None:
        sled_text = parsled.to_sled_mini(round_trip_input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert round_trip_expected_data == round_trip_data

    def test_round_trip_serializer(
        self,
        each_sled_serializer,
        round_trip_input_data: Dict[str, Dict[str, float]],
        round_trip_expected_data: Dict[str, Dict[str, Any]],
    ) -> None:
        sled_text = each_sled_serializer.to_sled(round_trip_input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert round_trip_expected_data == round_trip_data
