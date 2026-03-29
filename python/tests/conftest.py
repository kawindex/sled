from pathlib import Path

import pytest

import pysled


@pytest.fixture(scope="session")
def sled_test_data_dir() -> Path:
    return Path(__file__).parent.parent.parent.joinpath("testdata")


@pytest.fixture(scope="session")
def core_test_data_dir(sled_test_data_dir: Path) -> Path:
    return sled_test_data_dir.joinpath("core")


@pytest.fixture(
    scope="session",
    params=(
        pysled.SledSerializer,
        pysled.SledSerializerMini,
        pysled._serializer_basic.SledSerializerBasic,
    )
)
def each_sled_serializer(request: pytest.FixtureRequest):
    return request.param()


@pytest.fixture(scope="session")
def sled_serializer() -> pysled.SledSerializer:
    return pysled.SledSerializer()


@pytest.fixture(scope="session")
def sled_serializer_mini() -> pysled.SledSerializerMini:
    return pysled.SledSerializerMini()


@pytest.fixture(scope="session")
def sled_serializer_basic() -> pysled._serializer_basic.SledSerializerBasic:
    return pysled._serializer_basic.SledSerializerBasic()
