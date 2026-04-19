from pathlib import Path
from typing import Dict, NamedTuple

import pytest

import parsled


class IdentityStartTestData(NamedTuple):
    name: str
    expected_str: str


@pytest.fixture(scope="module", params=(True, False))
def identity_start_symbol_key_flag(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(scope="module")
def identity_start_symbol_data_dir(
    core_test_data_dir: Path,
    identity_start_symbol_key_flag: bool
) -> Path:
    dir_suffix = "key" if identity_start_symbol_key_flag else "value"
    dir_name = f"identity-start-symbol-{dir_suffix}"
    return core_test_data_dir.joinpath(dir_name)


@pytest.fixture(scope="module")
def identity_start_arbitrary_string() -> str:
    return "data"


@pytest.fixture(
    scope="class",
    params=(
        IdentityStartTestData(name="at", expected_str="@hello"),
        IdentityStartTestData(name="comma", expected_str=",hello"),
        IdentityStartTestData(name="dot", expected_str=".hello"),
        IdentityStartTestData(name="minus", expected_str="-hello"),
        IdentityStartTestData(name="plus", expected_str="+hello"),
        IdentityStartTestData(name="underscore", expected_str="_hello"),
        IdentityStartTestData(name="zero", expected_str="0hello"),
    ),
)
def identity_start_symbol_at_start_test_data(
    request: pytest.FixtureRequest
) -> IdentityStartTestData:
    return request.param


class TestIdentityStartSymbolAtStartOfIdentity:
    @pytest.fixture(
        scope="class",
        params=("identity", "concat-identity"),
    )
    def sled_path(
        self,
        request: pytest.FixtureRequest,
        identity_start_symbol_data_dir: Path,
        identity_start_symbol_at_start_test_data: IdentityStartTestData,
    ) -> Path:
        sled_file_name = f"{identity_start_symbol_at_start_test_data.name}.sd"
        return identity_start_symbol_data_dir.joinpath(
            f"{request.param}-start", sled_file_name
        )

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text()

    def test_parse(self, sled_text: str) -> None:
        with pytest.raises(parsled.SledError) as excinfo:
            parsled.from_sled(sled_text)
        assert parsled.SledErrorCategory.SYNTAX == excinfo.value.error_category


class TestIdentityStartSymbolAtStartOfQuote:
    @pytest.fixture(
        scope="class",
        params=(
            "single-quote",
            "double-quote",
            "concat-single-quote",
            "concat-double-quote",
        ),
    )
    def sled_path(
        self,
        request: pytest.FixtureRequest,
        identity_start_symbol_data_dir: Path,
        identity_start_symbol_at_start_test_data: IdentityStartTestData,
    ) -> Path:
        sled_file_name = f"{identity_start_symbol_at_start_test_data.name}.sd"
        return identity_start_symbol_data_dir.joinpath(
            f"{request.param}-start", sled_file_name
        )

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text()

    @pytest.fixture(scope="class")
    def expected_dict(
        self, 
        identity_start_symbol_at_start_test_data: IdentityStartTestData,
        identity_start_symbol_key_flag: bool,
        identity_start_arbitrary_string: str,
    ) -> Dict[str, str]:
        expected_str = identity_start_symbol_at_start_test_data.expected_str
        if identity_start_symbol_key_flag:
            return {expected_str: identity_start_arbitrary_string}
        else:
            return {identity_start_arbitrary_string: expected_str}

    def test_parse(
        self, sled_text: str, expected_dict: Dict[str, str]
    ) -> None:
        actual_dict = parsled.from_sled(sled_text)
        assert expected_dict == actual_dict


class TestIdentityStartSymbolInTail:
    @pytest.fixture(
        scope="class",
        params=(
            IdentityStartTestData(name="at", expected_str="hello@world"),
            IdentityStartTestData(name="comma", expected_str="hello,world"),
            IdentityStartTestData(name="dot", expected_str="example.com"),
            IdentityStartTestData(
                name="minus", expected_str="great-great-great-grandmother"
            ),
            IdentityStartTestData(name="plus", expected_str="one+two"),
            IdentityStartTestData(name="underscore", expected_str="hello_world"),
            IdentityStartTestData(name="zero", expected_str="o0o"),
        ),
    )
    def identity_start_symbol_in_tail_test_data(
        self, request: pytest.FixtureRequest
    ) -> IdentityStartTestData:
        return request.param

    @pytest.fixture(
        scope="class",
        params=(
            "identity",
            "single-quote",
            "double-quote",
            "concat-identity",
            "concat-single-quote",
            "concat-double-quote",
        )
    )
    def sled_path(
        self,
        request: pytest.FixtureRequest,
        identity_start_symbol_data_dir: Path,
        identity_start_symbol_in_tail_test_data: IdentityStartTestData,
    ) -> Path:
        sled_file_name = f"{identity_start_symbol_in_tail_test_data.name}.sd"
        return identity_start_symbol_data_dir.joinpath(
            f"{request.param}-tail", sled_file_name
        )

    @pytest.fixture(scope="class")
    def sled_text(self, sled_path: Path) -> str:
        return sled_path.read_text()

    @pytest.fixture(scope="class")
    def expected_dict(
        self,
        identity_start_symbol_in_tail_test_data: IdentityStartTestData,
        identity_start_symbol_key_flag: bool,
        identity_start_arbitrary_string: str,
    ) -> Dict[str, str]:
        expected_str = identity_start_symbol_in_tail_test_data.expected_str
        if identity_start_symbol_key_flag:
            return {expected_str: identity_start_arbitrary_string}
        else:
            return {identity_start_arbitrary_string: expected_str}

    def test_parse(self, sled_text: str, expected_dict: Dict[str, str]) -> None:
        actual_dict = parsled.from_sled(sled_text)
        assert expected_dict == actual_dict
