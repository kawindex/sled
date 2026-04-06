from pathlib import Path

import pytest

import parsled


@pytest.fixture(scope="session")
def sled_test_data_dir() -> Path:
    return Path(__file__).parent.parent.parent.joinpath("testdata")


@pytest.fixture(scope="session")
def core_test_data_dir(sled_test_data_dir: Path) -> Path:
    return sled_test_data_dir.joinpath("core")


@pytest.fixture(
    scope="session",
    params=(
        parsled.SledSerializer,
        parsled.SledSerializerMini,
        parsled._serializer_basic.SledSerializerBasic,
    )
)
def each_sled_serializer(request: pytest.FixtureRequest):
    return request.param()


@pytest.fixture(scope="session")
def sled_serializer() -> parsled.SledSerializer:
    return parsled.SledSerializer()


@pytest.fixture(scope="session")
def sled_serializer_mini() -> parsled.SledSerializerMini:
    return parsled.SledSerializerMini()


@pytest.fixture(scope="session")
def sled_serializer_basic() -> parsled._serializer_basic.SledSerializerBasic:
    return parsled._serializer_basic.SledSerializerBasic()
