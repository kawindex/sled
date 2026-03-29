from pathlib import Path
from typing import Dict, NamedTuple

import pytest

import pysled


class ImapDupTestCase(NamedTuple):
    file_name: str
    control_expected_imap: Dict[int, pysled.Entity]


class TestImapDup:
    @pytest.fixture(scope="class")
    def top_level_key(self) -> str:
        return "data"

    @pytest.fixture(scope="class")
    def imap_dup_data_dir(self, core_test_data_dir: Path) -> Path:
        return core_test_data_dir.joinpath("imap-dup")

    @pytest.fixture(scope="class")
    def invalid_data_dir(self, imap_dup_data_dir: Path) -> Path:
        return imap_dup_data_dir.joinpath("invalid")

    @pytest.fixture(scope="class")
    def control_data_dir(self, imap_dup_data_dir: Path) -> Path:
        return imap_dup_data_dir.joinpath("control")

    @pytest.fixture(scope="class", params=(
        ImapDupTestCase(
            file_name="basic.sd",
            control_expected_imap={123: "hello", 124: "world"},
        ),
        ImapDupTestCase(
            file_name="negative-zero.sd",
            control_expected_imap={-1: "", 0: ""},
        ),
        ImapDupTestCase(
            file_name="positive-sign.sd",
            control_expected_imap={
                8191: {"data": "base"},
                8192: ["database"],
            },
        ),
        ImapDupTestCase(
            file_name="underscore.sd",
            control_expected_imap={1193: "hello", 1194: "hello"},
        ),
        ImapDupTestCase(
            file_name="underscore-many.sd",
            control_expected_imap={216091: {}, 216092: []},
        ),
        ImapDupTestCase(
            file_name="underscore-leading.sd",
            control_expected_imap={-364_289: 1, -364_290: 0},
        ),
        ImapDupTestCase(
            file_name="underscore-leading-many.sd",
            control_expected_imap={704: [None], 705: [0, False]},
        ),
        ImapDupTestCase(
            file_name="underscore-mix.sd",
            control_expected_imap={1277: -1, 1278: 1},
        ),
        ImapDupTestCase(
            file_name="leading-zero.sd",
            control_expected_imap={2: "inline", 3: "key-value pairs"},
        ),
        ImapDupTestCase(
            file_name="leading-zero-many.sd",
            control_expected_imap={-17: 0, -18: 0},
        ),
        ImapDupTestCase(
            file_name="leading-mix.sd",
            control_expected_imap={-20: [], -21: True},
        ),
        ImapDupTestCase(
            file_name="mix.sd",
            control_expected_imap={
                1_812_433_253: {},
                272_559_682: {},
                -399_874: {},
                272_559_683: {},
                156: {},
            },
        ),
        ImapDupTestCase(
            file_name="mix-positive.sd",
            control_expected_imap={12_720_787: 12_72_07_87, 12_720_786: 0},
        ),
        ImapDupTestCase(
            file_name="mix-negative.sd",
            control_expected_imap={
                -1729: "Hello, World!",
                -1728: "Hello, World!",
            },
        ),
    ))
    def dup_test_case(self, request: pytest.FixtureRequest) -> ImapDupTestCase:
        return request.param

    @pytest.fixture(scope="class")
    def sled_file_name(self, dup_test_case: ImapDupTestCase) -> str:
        return dup_test_case.file_name

    @pytest.fixture(scope="class")
    def invalid_sled_path(
        self, invalid_data_dir: Path, sled_file_name: str
    ) -> Path:
        return invalid_data_dir.joinpath(sled_file_name)

    @pytest.fixture(scope="class")
    def invalid_sled_text(self, invalid_sled_path: Path) -> str:
        return invalid_sled_path.read_text().strip()

    def test_parse_invalid(self, invalid_sled_text: str) -> None:
        with pytest.raises(pysled.SledError) as excinfo:
            pysled.from_sled(invalid_sled_text)
        assert pysled.SledErrorCategory.DUPLICATE_MAP_KEY == excinfo.value.error_category

    @pytest.fixture(scope="class")
    def control_sled_path(
        self, control_data_dir: Path, sled_file_name: str
    ) -> Path:
        return control_data_dir.joinpath(sled_file_name)

    @pytest.fixture(scope="class")
    def control_sled_text(self, control_sled_path: Path) -> str:
        return control_sled_path.read_text().strip()

    @pytest.fixture(scope="class")
    def control_expected_dict(
        self, dup_test_case: ImapDupTestCase, top_level_key: str
    ) -> Dict[str, pysled.Entity]:
        return {top_level_key: dup_test_case.control_expected_imap}

    def test_parse_control(
        self,
        top_level_key: str,
        control_sled_text: str,
        control_expected_dict: Dict[str, pysled.Entity],
    ) -> None:
        actual_data = pysled.from_sled(control_sled_text)
        assert control_expected_dict == actual_data
        actual_imap = actual_data[top_level_key]
        for key in actual_imap:
            assert isinstance(key, int)

    def test_control_round_trip(
        self,
        top_level_key: str,
        control_expected_dict: Dict[str, pysled.Entity],
    ) -> None:
        sled_text = pysled.to_sled(control_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert control_expected_dict == round_trip_dict
        round_trip_imap = round_trip_dict[top_level_key]
        for key in round_trip_imap:
            assert isinstance(key, int)

    def test_control_round_trip_mini(
        self,
        top_level_key: str,
        control_expected_dict: Dict[str, pysled.Entity],
    ) -> None:
        sled_text = pysled.to_sled_mini(control_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert control_expected_dict == round_trip_dict
        round_trip_imap = round_trip_dict[top_level_key]
        for key in round_trip_imap:
            assert isinstance(key, int)

    def test_control_round_trip_basic(
        self,
        top_level_key: str,
        control_expected_dict: Dict[str, pysled.Entity],
    ) -> None:
        serializer = pysled._serializer_basic.SledSerializerBasic()
        sled_text = serializer.to_sled(control_expected_dict)
        round_trip_dict = pysled.from_sled(sled_text)
        assert control_expected_dict == round_trip_dict
        round_trip_imap = round_trip_dict[top_level_key]
        for key in round_trip_imap:
            assert isinstance(key, int)
