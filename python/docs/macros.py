import inspect
from pathlib import Path

import parsled

PYTHON_DIR = Path(__file__).parent.parent
PYTHON_README_PATH = PYTHON_DIR.joinpath("README.md")

REPO_DIR = PYTHON_DIR.parent
REPO_README_PATH = REPO_DIR.joinpath("README.md")

SLED_DIR = REPO_DIR.joinpath("sled")
SLED_GRAMMAR_PATH = SLED_DIR.joinpath("grammar.md")
SLED_SPEC_PATH = SLED_DIR.joinpath("spec.md")

SERIALIZER_MODULE_DOCSTRING = inspect.getdoc(parsled._serializer)
SERIALIZER_MINI_MODULE_DOCSTRING = inspect.getdoc(parsled._serializer_mini)


def assert_and_replace(
    base: str, target: str, replacement: str, count: int = 0
) -> str:
    if count > 0:
        assert base.count(target) == count
    return base.replace(target, replacement)


def make_sled_intro() -> str:
    s1 = assert_and_replace(
        base=REPO_README_PATH.read_text(encoding="utf-8", errors="strict"),
        target="[`parsled`](https://parsled.readthedocs.io)",
        replacement="[`parsled`](api.md)",
        count=1,
    )
    s2 = assert_and_replace(
        base=s1,
        target="[grammar](/sled/grammar.md)",
        replacement="[grammar](sled/grammar.md)",
        count=1,
    )
    return assert_and_replace(
        base=s2,
        target="[spec](/sled/spec.md)",
        replacement="[spec](sled/spec.md)",
        count=1,
    )


def define_env(env) -> None:
    env.variables["parsled_intro"] = assert_and_replace(
        base=PYTHON_README_PATH.read_text(encoding="utf-8", errors="strict"),
        target="https://parsled.readthedocs.io/en/stable/api/",
        replacement="api.md",
    )

    env.variables["sled_intro"] = make_sled_intro()

    env.variables["serialization_docstring"] = assert_and_replace(
        base=SERIALIZER_MODULE_DOCSTRING,
        target="`SledSerializer` documentation",
        replacement=(
            "[`SledSerializer` documentation]"
            "(api.md#parsled.SledSerializer)"
        ),
        count=1,
    )

    env.variables["mini_serialization_docstring"] = assert_and_replace(
        base=SERIALIZER_MINI_MODULE_DOCSTRING,
        target="their documentation",
        replacement="their [documentation](api.md#mini-serialization)",
        count=1,
    )

    env.variables["sled_grammar"] = SLED_GRAMMAR_PATH.read_text(
        encoding="utf-8", errors="strict"
    )

    env.variables["sled_spec"] = assert_and_replace(
        base=SLED_SPEC_PATH.read_text(encoding="utf-8", errors="strict"),
        target="[Grammar](/sled/grammar.md)",
        replacement="[Grammar](grammar.md)",
        count=1,
    )
