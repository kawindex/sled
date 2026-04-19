"""Script that runs some broad tests without any external dev dependency."""

import json
from pathlib import Path
from typing import Dict

import parsled


TEST_DATA_DIR = Path(__file__).parent.parent.parent.joinpath("testdata")

DEMO_DATA_DIR = TEST_DATA_DIR.joinpath("demo")
REPO_README_TEST_SLED_PATH = DEMO_DATA_DIR.joinpath("repo-readme.sd")
REPO_README_DEMO_EXPECTED_DATA = {
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


CHECKER_SUITE_TEST_DATA_DIR = TEST_DATA_DIR.joinpath("checker-suite")
CHECKER_SUITE_P01_JSON_PATH = CHECKER_SUITE_TEST_DATA_DIR.joinpath("p01.json")
CHECKER_SUITE_P01_SLED_PATH = CHECKER_SUITE_TEST_DATA_DIR.joinpath("p01.sd")


def test_parse(sled_text: str, expected_data: Dict[str, parsled.Entity]) -> None:
    actual_data = parsled.from_sled(sled_text)
    assert expected_data == actual_data


def test_round_trip(data: Dict[str, parsled.Entity]) -> None:
    sled_text = parsled.to_sled(data)
    round_trip_data = parsled.from_sled(sled_text)
    assert data == round_trip_data


def test_round_trip_mini(data: Dict[str, parsled.Entity]) -> None:
    sled_text = parsled.to_sled_mini(data)
    round_trip_data = parsled.from_sled(sled_text)
    assert data == round_trip_data


if __name__ == "__main__":
    print("Start smoke test...")

    # repo readme demo
    test_parse(
        sled_text=REPO_README_TEST_SLED_PATH.read_text(encoding="utf-8"),
        expected_data=REPO_README_DEMO_EXPECTED_DATA,
    )
    test_round_trip(REPO_README_DEMO_EXPECTED_DATA)
    test_round_trip_mini(REPO_README_DEMO_EXPECTED_DATA)

    # checker suite p01
    checker_suite_p01_json_text = CHECKER_SUITE_P01_JSON_PATH.read_text()
    checker_suite_p01_expected_dict = {
        "content": json.loads(checker_suite_p01_json_text)
    }
    test_parse(
        sled_text=CHECKER_SUITE_P01_SLED_PATH.read_text(),
        expected_data=checker_suite_p01_expected_dict,
    )
    test_round_trip(checker_suite_p01_expected_dict)
    test_round_trip_mini(checker_suite_p01_expected_dict)

    print("Smoke test complete. Success!")
