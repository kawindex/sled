from pathlib import Path
from typing import Any, Dict, Mapping, NamedTuple

import pytest

import parsled


class DemoTestCase(NamedTuple):
    file_name: str
    expected_data: Dict[str, parsled.Entity]


@pytest.fixture(scope="module")
def demo_data_dir(sled_test_data_dir: Path) -> Path:
    return sled_test_data_dir.joinpath("demo")


class TestDemo:
    @pytest.fixture(
        scope="class",
        params=(
            DemoTestCase(
                file_name="python-parser.sd",
                expected_data={
                    "name": "John Doe",
                    "age": 50,
                    "children": ["Jack", "Jill"],
                },
            ),
            DemoTestCase(
                file_name="python-serializer.sd",
                expected_data={
                    "name": "John Doe",
                    "age": 50,
                    "children": ["Jack", "Jill"],
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
        return sled_path.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def expected_data(
        self, demo_test_case: DemoTestCase
    ) -> Dict[str, parsled.Entity]:
        return demo_test_case.expected_data

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        actual_data = parsled.from_sled(sled_text)
        assert expected_data == actual_data

    def test_round_trip(
        self, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        sled_text = parsled.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_mini(
        self, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        sled_text = parsled.to_sled_mini(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer(
        self, each_sled_serializer, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        sled_text = each_sled_serializer.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data


class TestRepoReadme:
    @pytest.fixture(scope="class")
    def sled_path(self, demo_data_dir: Path) -> Path:
        return demo_data_dir.joinpath("repo-readme.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, parsled.Entity]:
        return {
            "my_string": "use quotes if you have spaces or other special cases",
            "another_string": "otherwise_quotes_are_optional",
            "my_integer": 123,
            "my_float": 4.5,
            "boolean_true": True,
            "boolean_false": False,
            "distinguished_nil": None,
            "my_list": [ "Lorem ipsum", 3.14, False ],
            "This is a smap. Each key is a string. (The root level is itself a smap.)": {
                "something": "xyz",
                "another thing": True,
            },
            "This is an imap. Each key is an integer.": { 3: None, -100: 4.0 },
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
        }

    def test_parse(
        self, sled_text: str, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        actual_data = parsled.from_sled(sled_text)
        assert expected_data == actual_data

    def test_round_trip(
        self, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        sled_text = parsled.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_mini(
        self, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        sled_text = parsled.to_sled_mini(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer(
        self, each_sled_serializer, expected_data: Dict[str, parsled.Entity]
    ) -> None:
        sled_text = each_sled_serializer.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_with_ser_kwargs(
        self,
        expected_data: Dict[str, parsled.Entity],
        sled_serializer_kwargs: Mapping[str, Any],
    ) -> None:
        sled_text = parsled.to_sled(expected_data, **sled_serializer_kwargs)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_mini_with_ser_kwargs(
        self,
        expected_data: Dict[str, parsled.Entity],
        sled_serializer_mini_kwargs: Mapping[str, Any],
    ) -> None:
        sled_text = parsled.to_sled_mini(
            expected_data, **sled_serializer_mini_kwargs
        )
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer_with_kwargs(
        self,
        sled_serializer_with_kwargs: parsled.SledSerializer,
        expected_data: Dict[str, parsled.Entity],
    ) -> None:
        sled_text = sled_serializer_with_kwargs.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer_mini_with_kwargs(
        self,
        sled_serializer_mini_with_kwargs: parsled.SledSerializerMini,
        expected_data: Dict[str, parsled.Entity],
    ) -> None:
        sled_text = sled_serializer_mini_with_kwargs.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer_basic_with_kwargs(
        self,
        sled_serializer_basic_with_kwargs: parsled._serializer_basic.SledSerializerBasic,
        expected_data: Dict[str, parsled.Entity],
    ) -> None:
        sled_text = sled_serializer_basic_with_kwargs.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data
