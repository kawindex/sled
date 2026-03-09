"""
Tests based on JSON_checker test suite from:
https://json.org/JSON_checker/
"""

import json
from pathlib import Path
from typing import Dict, NamedTuple

import pytest

import pysled


class CheckerSuiteTestCase(NamedTuple):
    sled_file_name: str
    expected_data: Dict[str, pysled.Entity]


@pytest.fixture(scope="module")
def checker_suite_data_dir(sled_test_data_dir: Path) -> Path:
    return sled_test_data_dir.joinpath("checker-suite")


class TestCheckerSuiteP01:

    @pytest.fixture(scope="class")
    def arbitrary_key(self) -> str:
        return "content"

    @pytest.fixture(scope="class")
    def json_path(self, checker_suite_data_dir: Path) -> Path:
        return checker_suite_data_dir.joinpath("p01.json")

    @pytest.fixture(scope="class")
    def json_text(self, json_path: Path) -> str:
        return json_path.read_text().strip()

    @pytest.fixture(scope="class")
    def json_data(self, json_text: Path) -> list:
        return json.loads(json_text)

    @pytest.fixture(scope="class")
    def expected_dict(
        self, json_data: list, arbitrary_key: str
    ) -> Dict[str, list]:
        return {arbitrary_key: json_data}

    @pytest.fixture(scope="class", params=("p01.sd", "p01-mini.sd"))
    def sled_file_name(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(scope="class")
    def sled_path(
        self, checker_suite_data_dir: Path, sled_file_name: str
    ) -> Path:
        return checker_suite_data_dir.joinpath(sled_file_name)

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_parse(
        self, sled_text: str, expected_dict: Dict[str, list]
    ) -> None:
        actual_dict = pysled.from_sled(sled_text)
        assert expected_dict == actual_dict

    def test_round_trip(self, expected_dict: Dict[str, list]) -> None:
        sled_text = pysled.to_sled(expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert expected_dict == round_trip_dict

    def test_round_trip_mini(self, expected_dict: Dict[str, list]) -> None:
        sled_text = pysled.to_sled_mini(expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert expected_dict == round_trip_dict


# Invalid Sled

class TestCheckerSuiteInvalid:

    @pytest.fixture(
        scope="class",
        params=(
            CheckerSuiteTestCase(
                sled_file_name="f01.sd",
                expected_data={"key": "A Sled document should be a map (at the top level), not a string."},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f02.sd",
                expected_data={"key": ["Unclosed array"]},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f07.sd",
                expected_data={"anything": "outside of top-level enclosing braces"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f08.sd",
                expected_data={"extra close": []},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f10.sd",
                expected_data={"Extra value after close": True},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f11.sd",
                expected_data={"Illegal expression": [2]},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f12.sd",
                expected_data={"Illegal_invocation": "alert"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f14.sd",
                expected_data={"Numbers cannot be hex": b'\x14'},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f15.sd",
                expected_data={"Illegal_backslash_escape": "\x15"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f16.sd",
                expected_data={"unquoted_escape": "\nest"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f17.sd",
                expected_data={"Illegal backslash escape": "\017"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f19.sd",
                expected_data={"data": {"Missing equal": None}},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f20.sd",
                expected_data={"double_equal": False},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f21.sd",
                expected_data={"data": {"semicolon instead of equal": None}},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f22.sd",
                expected_data={"x": ["equal instead of delimiter", False]},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f23.sd",
                expected_data={"bad value": True},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f26.sd",
                expected_data={
                    "invalid escape": "tab\\\tcharacter\\\tin\\\tstring\\  ",
                    "proper escape": "tab	character	in	string\\  ",
                    "both": r"tab\	character\	in\	string\  ",
                },
            ),
            CheckerSuiteTestCase(
                sled_file_name="f27.sd",
                expected_data={"use_escape": "line\nbreak"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f28.sd",
                expected_data={"use @concat": "linebreak"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f29.sd",
                expected_data={"post-exponent": 0.0},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f30.sd",
                expected_data={"exp_digits": 0.0},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f31.sd",
                expected_data={"see the signs!": 0.0},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f32.sd",
                expected_data={"delimiter": {"instead of closing brace": True}},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f33.sd",
                expected_data={"what_this": ["mismatch"]},
            ),
        )
    )
    def invalid_test_case(
        self, request: pytest.FixtureRequest
    ) -> CheckerSuiteTestCase:
        return request.param

    @pytest.fixture(scope="class")
    def invalid_sled_dir(self, checker_suite_data_dir: Path) -> Path:
        return checker_suite_data_dir.joinpath("invalid-sled-invalid")

    @pytest.fixture(scope="class")
    def invalid_sled_path(
        self,
        invalid_sled_dir: Path,
        invalid_test_case: CheckerSuiteTestCase,
    ) -> Path:
        return invalid_sled_dir.joinpath(invalid_test_case.sled_file_name)

    @pytest.fixture(scope="class")
    def invalid_sled_text(self, invalid_sled_path: Path) -> str:
        return invalid_sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def control_sled_dir(self, checker_suite_data_dir: Path) -> Path:
        return checker_suite_data_dir.joinpath("invalid-sled-control")

    @pytest.fixture(scope="class")
    def control_sled_path(
        self,
        control_sled_dir: Path,
        invalid_test_case: CheckerSuiteTestCase,
    ) -> Path:
        return control_sled_dir.joinpath(invalid_test_case.sled_file_name)

    @pytest.fixture(scope="class")
    def control_sled_text(self, control_sled_path: Path) -> str:
        return control_sled_path.read_text().strip()

    def test_parse_invalid(self, invalid_sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(invalid_sled_text)
        assert pysled.SledErrorCategory.SYNTAX == excinfo.value.error_category

    def test_parse_control(
        self, invalid_test_case: CheckerSuiteTestCase, control_sled_text: str
    ) -> None:
        actual_data = pysled.from_sled(control_sled_text)
        assert invalid_test_case.expected_data == actual_data

    def test_control_round_trip(
        self, invalid_test_case: CheckerSuiteTestCase
    ) -> None:
        sled_text = pysled.to_sled(invalid_test_case.expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert invalid_test_case.expected_data == round_trip_data

    def test_control_round_trip_mini(
        self, invalid_test_case: CheckerSuiteTestCase
    ) -> None:
        sled_text = pysled.to_sled_mini(invalid_test_case.expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert invalid_test_case.expected_data == round_trip_data


# Valid Sled

class TestCheckerSuiteValid:
    @pytest.fixture(scope="class")
    def valid_sled_dir(self, checker_suite_data_dir: Path) -> Path:
        return checker_suite_data_dir.joinpath("valid-sled")

    @pytest.fixture(
        scope="class",
        params=(
            CheckerSuiteTestCase(
                sled_file_name="f03.sd",
                expected_data={
                    "unquoted_key": "keys don't always have to be quoted"
                },
            ),
            CheckerSuiteTestCase(
                sled_file_name="f04.sd",
                expected_data={"my_list": ["trailing_semicolon"]},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f05.sd",
                expected_data={"toil and trouble": ["2x_extra_delimiter"]},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f06.sd",
                expected_data={"ft_bug": ["<-- missing value"]},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f09.sd",
                expected_data={"extra_delimiter": {"key": True}},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f13.sd",
                expected_data={
                    "integers CAN have leading zeroes": 13,
                    "so CAN floats": 26.34,
                },
            ),
            CheckerSuiteTestCase(
                sled_file_name="f14.sd",
                expected_data={"hex": b"\x14"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f15.sd",
                expected_data={"Legal_backslash_escape": "\u0015"},
            ),
            CheckerSuiteTestCase(
                sled_file_name="f18.sd",
                expected_data={
                    "arbitrary_finite_depth!":
                    [[[[[[[[[[[[[[[[[[[["not too deep"]]]]]]]]]]]]]]]]]]]],
                },
            ),
            CheckerSuiteTestCase(
                sled_file_name="f24.sd",
                expected_data={
                    "single": "quote", "double": "quote", "bare": "bones"
                },
            ),
            CheckerSuiteTestCase(
                sled_file_name="f25.sd",
                expected_data={
                    "prefer to escape": "\ttab\tcharacter\tin\tstring\t"
                },
            ),
        ),
    )
    def valid_test_case(
        self, request: pytest.FixtureRequest
    ) -> CheckerSuiteTestCase:
        return request.param

    @pytest.fixture(scope="class")
    def sled_path(
        self, valid_sled_dir: Path, valid_test_case: CheckerSuiteTestCase
    ) -> Path:
        return valid_sled_dir.joinpath(valid_test_case.sled_file_name)

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text().strip()

    def test_parse(
        self, valid_test_case: CheckerSuiteTestCase, sled_text: str
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert valid_test_case.expected_data == actual_data

    def test_round_trip(
        self, valid_test_case: CheckerSuiteTestCase
    ) -> None:
        sled_text = pysled.to_sled(valid_test_case.expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert valid_test_case.expected_data == round_trip_data

    def test_round_trip_mini(
        self, valid_test_case: CheckerSuiteTestCase
    ) -> None:
        sled_text = pysled.to_sled_mini(valid_test_case.expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert valid_test_case.expected_data == round_trip_data
