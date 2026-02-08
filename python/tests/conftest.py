from pathlib import Path

import pytest


@pytest.fixture(scope="package")
def sled_test_data_dir() -> Path:
    return Path(__file__).parent.parent.parent.joinpath("testdata")


@pytest.fixture(scope="package")
def core_test_data_dir(sled_test_data_dir: Path) -> Path:
    return sled_test_data_dir.joinpath("core")
