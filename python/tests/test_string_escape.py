from pathlib import Path
from typing import Dict, NamedTuple

import pytest

import pysled


class StringEscapeTestCase(NamedTuple):
    position_dir_name: str
    file_name: str
    expected_str: str


@pytest.fixture(
    scope="module",
    params=(
        StringEscapeTestCase(
            position_dir_name="alone",
            file_name="backslash.sd",
            expected_str="\\",
        ),
        StringEscapeTestCase(
            position_dir_name="alone",
            file_name="CR.sd",
            expected_str="\r",
        ),
        StringEscapeTestCase(
            position_dir_name="alone",
            file_name="LF.sd",
            expected_str="\n",
        ),
        StringEscapeTestCase(
            position_dir_name="alone",
            file_name="tab.sd",
            expected_str="\t",
        ),
        StringEscapeTestCase(
            position_dir_name="alone",
            file_name="single-quote.sd",
            expected_str="'",
        ),
        StringEscapeTestCase(
            position_dir_name="alone",
            file_name="double-quote.sd",
            expected_str='"',
        ),
        StringEscapeTestCase(
            position_dir_name="alone",
            file_name="unicode.sd",
            expected_str="🛷",
        ),
        StringEscapeTestCase(
            position_dir_name="start",
            file_name="backslash.sd",
            expected_str="\\hello",
        ),
        StringEscapeTestCase(
            position_dir_name="start",
            file_name="CR.sd",
            expected_str="\rhello",
        ),
        StringEscapeTestCase(
            position_dir_name="start",
            file_name="LF.sd",
            expected_str="\nhello",
        ),
        StringEscapeTestCase(
            position_dir_name="start",
            file_name="tab.sd",
            expected_str="\thello",
        ),
        StringEscapeTestCase(
            position_dir_name="start",
            file_name="single-quote.sd",
            expected_str="'hello",
        ),
        StringEscapeTestCase(
            position_dir_name="start",
            file_name="double-quote.sd",
            expected_str='"hello',
        ),
        StringEscapeTestCase(
            position_dir_name="start",
            file_name="unicode.sd",
            expected_str="{hello",
        ),
        StringEscapeTestCase(
            position_dir_name="middle",
            file_name="backslash.sd",
            expected_str="hello\\world",
        ),
        StringEscapeTestCase(
            position_dir_name="middle",
            file_name="CR.sd",
            expected_str="hello\rworld",
        ),
        StringEscapeTestCase(
            position_dir_name="middle",
            file_name="LF.sd",
            expected_str="hello\nworld",
        ),
        StringEscapeTestCase(
            position_dir_name="middle",
            file_name="tab.sd",
            expected_str="hello\tworld",
        ),
        StringEscapeTestCase(
            position_dir_name="middle",
            file_name="single-quote.sd",
            expected_str="hello'world",
        ),
        StringEscapeTestCase(
            position_dir_name="middle",
            file_name="double-quote.sd",
            expected_str='hello"world',
        ),
        StringEscapeTestCase(
            position_dir_name="middle",
            file_name="unicode.sd",
            expected_str="hello\x03world",
        ),
        StringEscapeTestCase(
            position_dir_name="end",
            file_name="backslash.sd",
            expected_str="hello\\",
        ),
        StringEscapeTestCase(
            position_dir_name="end",
            file_name="CR.sd",
            expected_str="hello\r",
        ),
        StringEscapeTestCase(
            position_dir_name="end",
            file_name="LF.sd",
            expected_str="hello\n",
        ),
        StringEscapeTestCase(
            position_dir_name="end",
            file_name="tab.sd",
            expected_str="hello\t",
        ),
        StringEscapeTestCase(
            position_dir_name="end",
            file_name="single-quote.sd",
            expected_str="hello'",
        ),
        StringEscapeTestCase(
            position_dir_name="end",
            file_name="double-quote.sd",
            expected_str='hello"',
        ),
        StringEscapeTestCase(
            position_dir_name="end",
            file_name="unicode.sd",
            expected_str="hello?",
        ),
    ),
)
def string_escape_test_case(
    request: pytest.FixtureRequest
) -> StringEscapeTestCase:
    return request.param


class TestStringEscapeValue:
    @pytest.fixture(scope="class")
    def arbitrary_key(self) -> str:
        return "data"

    @pytest.fixture(scope="class")
    def string_escape_value_test_data_dir(
        self, core_test_data_dir: Path
    ) -> Path:
        return core_test_data_dir.joinpath("string-escape-value")

    @pytest.fixture(scope="class", params=("", "concat-"))
    def identity_sub_dir(
        self,
        request: pytest.FixtureRequest,
        string_escape_value_test_data_dir: Path,
    ) -> Path:
        sub_dir_name = f"{request.param}identity"
        return string_escape_value_test_data_dir.joinpath(sub_dir_name)

    @pytest.fixture(scope="class")
    def identity_sled_path(
        self,
        identity_sub_dir: Path,
        string_escape_test_case: StringEscapeTestCase,
    ) -> Path:
        return identity_sub_dir.joinpath(
            string_escape_test_case.position_dir_name,
            string_escape_test_case.file_name,
        )

    @pytest.fixture(scope="class")
    def identity_sled_text(self, identity_sled_path: Path) -> str:
        return identity_sled_path.read_text()

    def test_identity_parse(self, identity_sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(identity_sled_text)
        assert pysled.SledErrorCategory.SYNTAX == excinfo.value.error_category

    @pytest.fixture(scope="class", params=("", "concat-"))
    def quote_sub_dir_prefix(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(
        scope="class",
        params=("single-quote", "double-quote"),
    )
    def quote_sub_dir(
        self,
        request: pytest.FixtureRequest,
        string_escape_value_test_data_dir: Path,
        quote_sub_dir_prefix: str,
    ) -> Path:
        sub_dir_name = f"{quote_sub_dir_prefix}{request.param}"
        return string_escape_value_test_data_dir.joinpath(sub_dir_name)

    @pytest.fixture(scope="class")
    def quote_sled_path(
        self,
        quote_sub_dir: Path,
        string_escape_test_case: StringEscapeTestCase,
    ) -> Path:
        return quote_sub_dir.joinpath(
            string_escape_test_case.position_dir_name,
            string_escape_test_case.file_name,
        )

    @pytest.fixture(scope="class")
    def quote_sled_text(self, quote_sled_path: Path) -> str:
        return quote_sled_path.read_text()

    @pytest.fixture(scope="class")
    def quote_expected_dict(
        self,
        arbitrary_key: str,
        string_escape_test_case: StringEscapeTestCase,
    ) -> Dict[str, str]:
        return {arbitrary_key: string_escape_test_case.expected_str}

    def test_quote_parse(
        self, quote_sled_text: str, quote_expected_dict: Dict[str, str]
    ) -> None:
        actual_dict = pysled.from_sled(quote_sled_text)
        assert quote_expected_dict == actual_dict

    def test_quote_round_trip(
        self, quote_expected_dict: Dict[str, str]
    ) -> None:
        sled_text = pysled.to_sled(quote_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert quote_expected_dict == round_trip_dict

    def test_quote_round_trip_mini(
        self, quote_expected_dict: Dict[str, str]
    ) -> None:
        sled_text = pysled.to_sled_mini(quote_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert quote_expected_dict == round_trip_dict

    def test_quote_round_trip_serializer(
        self, each_sled_serializer, quote_expected_dict: Dict[str, str]
    ) -> None:
        sled_text = each_sled_serializer.to_sled(quote_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert quote_expected_dict == round_trip_dict


class TestStringEscapeKey:
    @pytest.fixture(scope="class")
    def arbitrary_value(self) -> str:
        return "data"

    @pytest.fixture(scope="class")
    def string_escape_key_test_data_dir(
        self, core_test_data_dir: Path
    ) -> Path:
        return core_test_data_dir.joinpath("string-escape-key")

    @pytest.fixture(scope="class", params=("", "concat-"))
    def identity_sub_dir(
        self,
        request: pytest.FixtureRequest,
        string_escape_key_test_data_dir: Path,
    ) -> Path:
        sub_dir_name = f"{request.param}identity"
        return string_escape_key_test_data_dir.joinpath(sub_dir_name)

    @pytest.fixture(scope="class")
    def identity_sled_path(
        self,
        identity_sub_dir: Path,
        string_escape_test_case: StringEscapeTestCase,
    ) -> Path:
        return identity_sub_dir.joinpath(
            string_escape_test_case.position_dir_name,
            string_escape_test_case.file_name,
        )

    @pytest.fixture(scope="class")
    def identity_sled_text(self, identity_sled_path: Path) -> str:
        return identity_sled_path.read_text()

    def test_identity_parse(self, identity_sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(identity_sled_text)
        assert pysled.SledErrorCategory.SYNTAX == excinfo.value.error_category

    @pytest.fixture(scope="class", params=("", "concat-"))
    def quote_sub_dir_prefix(self, request: pytest.FixtureRequest) -> str:
        return request.param

    @pytest.fixture(
        scope="class",
        params=("single-quote", "double-quote"),
    )
    def quote_sub_dir(
        self,
        request: pytest.FixtureRequest,
        string_escape_key_test_data_dir: Path,
        quote_sub_dir_prefix: str,
    ) -> Path:
        sub_dir_name = f"{quote_sub_dir_prefix}{request.param}"
        return string_escape_key_test_data_dir.joinpath(sub_dir_name)

    @pytest.fixture(scope="class")
    def quote_sled_path(
        self,
        quote_sub_dir: Path,
        string_escape_test_case: StringEscapeTestCase,
    ) -> Path:
        return quote_sub_dir.joinpath(
            string_escape_test_case.position_dir_name,
            string_escape_test_case.file_name,
        )

    @pytest.fixture(scope="class")
    def quote_sled_text(self, quote_sled_path: Path) -> str:
        return quote_sled_path.read_text()

    @pytest.fixture(scope="class")
    def quote_expected_dict(
        self,
        arbitrary_value: str,
        string_escape_test_case: StringEscapeTestCase,
    ) -> Dict[str, str]:
        return {string_escape_test_case.expected_str: arbitrary_value}

    def test_quote_parse(
        self, quote_sled_text: str, quote_expected_dict: Dict[str, str]
    ) -> None:
        actual_dict = pysled.from_sled(quote_sled_text)
        assert quote_expected_dict == actual_dict

    def test_quote_round_trip(
        self, quote_expected_dict: Dict[str, str]
    ) -> None:
        sled_text = pysled.to_sled(quote_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert quote_expected_dict == round_trip_dict

    def test_quote_round_trip_mini(
        self, quote_expected_dict: Dict[str, str]
    ) -> None:
        sled_text = pysled.to_sled_mini(quote_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert quote_expected_dict == round_trip_dict

    def test_quote_round_trip_serializer(
        self, each_sled_serializer, quote_expected_dict: Dict[str, str]
    ) -> None:
        sled_text = each_sled_serializer.to_sled(quote_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert quote_expected_dict == round_trip_dict
