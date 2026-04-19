from pathlib import Path
from typing import Dict

import pytest

import parsled


class TestConcat:

    @pytest.fixture(scope="class")
    def sled_path(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("concat-basic.sd")

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text()

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, parsled.Entity]:
        return {
            "my_concat": (
                "Constituent quotes are concatenated as-is, "
                "without any delimiter, so include spaces and "
                "line separators as desired.\n"
                "\nHere's a new paragraph. Each segment is just "
                "a normal quote or identity, so you can of course "
                "have multiple\nline\n"
                "separators,\n"
                "wherever.\n"
                "\n"
                "Like in maps and lists, adjacent segments are separated by "
                "at least one semicolon or line separator.\nYou can have "
                "stray delimiters or line separators anywhere\n"
                "this_also_works_just_fine_subject_to_the_usual_restrictions\n"
                "You_still_have_to_quote spaces if you want to use them."
            ),
            (
                "These work just fine as keys.\nThey are equivalent to "
                "any other string representation of their concatenated form"
            ): "my_entity_value",
            "squeezesquish": "mini",
            "this is empty": "",
            "same": "",
            "again": "",
            "Lorem ipsum": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
                "eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                "laboris nisi ut aliquip ex ea commodo consequat. Duis aute "
                "irure dolor in reprehenderit in voluptate velit esse cillum "
                "dolore eu fugiat nulla pariatur. Excepteur sint occaecat "
                "cupidatat non proident, sunt in culpa qui officia deserunt "
                "mollit anim id est laborum."
            ),
            "Linem ipsum": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit,\nsed do "
                "eiusmod tempor incididunt ut labore et dolore magna aliqua.\n"
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                "laboris\r\nnisi ut aliquip ex ea commodo consequat. Duis aute "
                "irure dolor in\r\nreprehenderit in voluptate velit esse cillum "
                "dolore eu fugiat nulla pariatur.\nExcepteur sint occaecat "
                "cupidatat non proident,\rsunt in culpa qui officia deserunt "
                "mollit anim id est laborum.\n\r"
            ),
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
        # This doesn't actually serialize to `concat` though.
        sled_text = parsled.to_sled_mini(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer(
        self,
        each_sled_serializer,
        expected_data: Dict[str, parsled.Entity],
    ) -> None:
        # `SledSerializerMini` and `SledSerializerBasic` don't actually
        # serialize to `concat` though.
        sled_text = each_sled_serializer.to_sled(expected_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data
