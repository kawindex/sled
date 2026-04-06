"""Each keyword that denotes a single particular value."""

import dataclasses
import math
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from parsled.spec import KEYWORD_MARK, Entity


@dataclasses.dataclass(frozen=True)
class KeywordLiteralSpec:
    name: str
    lexeme: str = dataclasses.field(init=False)
    evaluation: Entity

    def __post_init__(self) -> None:
        object.__setattr__(self, "lexeme", f"{KEYWORD_MARK}{self.name}")


class KeywordLiteral(Enum):
    NAN = KeywordLiteralSpec("nan", math.nan)
    INF = KeywordLiteralSpec("inf", math.inf)
    NINF = KeywordLiteralSpec("ninf", -math.inf)
    TRUE = KeywordLiteralSpec("true", True)
    FALSE = KeywordLiteralSpec("false", False)
    NIL = KeywordLiteralSpec("nil", None)


KEYWORD_LITERALS: Mapping[str, KeywordLiteralSpec] = MappingProxyType({
    keyword_literal.value.name: keyword_literal.value
    for keyword_literal in KeywordLiteral.__members__.values()
})
