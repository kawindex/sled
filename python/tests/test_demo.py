from pathlib import Path
from typing import Dict, NamedTuple

import pytest

import pysled


class DemoTestCase(NamedTuple):
    file_name: str
    expected_data: Dict[str, pysled.Entity]


class TestDemo:
    @pytest.fixture(scope="class")
    def demo_data_dir(self, sled_test_data_dir: Path) -> Path:
        return sled_test_data_dir.joinpath("demo")

    @pytest.fixture(
        scope="class",
        params=(
            DemoTestCase(
                file_name="repo-readme.sd",
                expected_data={
                    "my_string": "use quotes if you have spaces or other special cases",
                    "another_string": "otherwise_quotes_are_optional",
                    "my_integer": 123,
                    "my_float": 4.5,
                    "boolean_true": True,
                    "boolean_false": False,
                    "distinguished_nil": None,
                    "my_list": [ "Lorem ipsum", 3.14, False ],
                    "The smap has string keys (the root level is itself a smap).": {
                        "something": "xyz",
                        "another thing": True,
                    },
                    "The imap has integer keys.": { 3: None, -100: 4.0 },
                    "colors": [
                        "orange", "red", "green", "yellow",
                        "purple", "brown", "blue", "pink",
                    ],
                    "grocery_store": [
                        {
                            "name": "avocado",
                            "in_stock": True,
                            "price": 1.29,
                            "buyers": [ "Alice", "Bob" ],
                        },
                        { "name": "banana", "in_stock": True, "price": 0.15, "buyers": [] },
                        { "name": "coconut", "in_stock": False, "price": 2.97, "buyers": [] },
                    ],
                    "Supports most of Unicode?": {
                        "English": "Yes!",
                        "español": "¡Sí!",
                        "中文": "是的！",
                        "emoji": "✅🎉",
                    },
                },
            ),
        ),
    )
    def demo_test_case(self, request: pytest.FixtureRequest) -> DemoTestCase:
        return request.param

    @pytest.fixture(scope="class")
    def sled_path(self, demo_data_dir: Path, demo_test_case: DemoTestCase) -> Path:
        return demo_data_dir.joinpath(demo_test_case.file_name)

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text(encoding="utf-8").strip()

    @pytest.fixture(scope="class")
    def expected_data(
        self, demo_test_case: DemoTestCase
    ) -> Dict[str, pysled.Entity]:
        return demo_test_case.expected_data

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        actual_data = pysled.from_sled(sled_text)
        assert expected_data == actual_data

    def test_round_trip(
        self, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        sled_text = pysled.to_sled(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_mini(
        self, expected_data: Dict[str, pysled.Entity]
    ) -> None:
        sled_text = pysled.to_sled_mini(expected_data)
        round_trip_data = pysled.from_sled(sled_text)
        assert expected_data == round_trip_data
