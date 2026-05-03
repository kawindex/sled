import dataclasses
from typing import Any, Dict, List, NamedTuple

import pytest

import parsled


class Point(NamedTuple):
    name: str
    x: int
    y: int

    def to_sled_serializable(self) -> List[int]:
        return [self.x, self.y]


@dataclasses.dataclass(frozen=True)
class RectangleByVertex:
    lo_lo: Point
    lo_hi: Point
    hi_lo: Point
    hi_hi: Point
    _area: int


class Rectangle:
    def __init__(
        self, x_lo: int, y_lo: int, x_length: int, y_length: int
    ) -> None:
        self.x_lo = x_lo
        self.y_lo = y_lo
        self.x_length = x_length
        self.y_length = y_length

    def to_sled_serializable(self) -> RectangleByVertex:
        x_hi = self.x_lo + self.x_length
        y_hi = self.y_lo + self.y_length
        return RectangleByVertex(
            lo_lo=Point("xyz", self.x_lo, self.y_lo),
            lo_hi=Point("a for arbitrary", self.x_lo, y_hi),
            hi_lo=Point("d", x_hi, self.y_lo),
            hi_hi=Point("bc", x_hi, y_hi),
            _area=self.x_length * self.y_length,
        )


class RectangleTestCase(NamedTuple):
    input_data: Rectangle
    expected_data: Dict[str, Any]


class TestRectangle:
    @pytest.fixture(scope="class")
    def input_data(self) -> Rectangle:
        return Rectangle(3, 0, 8, 25)

    @pytest.fixture(scope="class")
    def expected_data(self) -> Dict[str, List[int]]:
        return {
            "lo_lo": [3, 0],
            "lo_hi": [3, 25],
            "hi_lo": [11, 0],
            "hi_hi": [11, 25],
            "_area": 200,
        }

    def test_round_trip(
        self, input_data: Rectangle, expected_data: Dict[str, List[int]]
    ) -> None:
        sled_text = parsled.to_sled(input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_mini(
        self, input_data: Rectangle, expected_data: Dict[str, List[int]]
    ) -> None:
        sled_text = parsled.to_sled_mini(input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data

    def test_round_trip_serializer(
        self,
        each_sled_serializer,
        input_data: Rectangle,
        expected_data: Dict[str, List[int]],
    ) -> None:
        sled_text = each_sled_serializer.to_sled(input_data)
        round_trip_data = parsled.from_sled(sled_text)
        assert expected_data == round_trip_data
