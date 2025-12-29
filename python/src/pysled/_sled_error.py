from collections import defaultdict
from enum import Enum
from typing import DefaultDict, List, Tuple, TypeVar, Union

from pysled._parser_metadata import ParseSnapshot
from pysled.spec import DEFAULT_LINE_SEPARATOR, HORIZONTAL_SPACE_SET


ERROR_POINTER_CHAR = "^"
ERROR_ELLIPSIS = "..."

MAX_ERROR_CONTEXT_LEN = 80
"""
The maximum number of characters around the invalid input
to include in the error message.

Error messages will attempt to display the entire line
containing the invalid input.
However, if the part of the line before the invalid input
is longer than this, then it will be truncated such that
only the substring of this length adjacent to the invalid input
will be included.
The same applies to the part of the line after the invalid input.
"""

_SPACE = " "


class SledErrorCategory(Enum):
    SYNTAX = "syntax"
    MAP_KEY_TYPE = "map key type"
    DUPLICATE_MAP_KEY = "duplicate map key"
    NUMBER_RANGE = "number range"


class SledError(Exception):
    """Indicates a failure to parse a part of the input text."""

    Self = TypeVar("Self", bound="SledError")

    def __init__(
        self,
        error_message: str,
        *,
        error_category: SledErrorCategory = SledErrorCategory.SYNTAX,
        reason: str,
        start_line_num: int,
    ) -> None:
        """
        Args:
            error_message:
                The formatted error message to be displayed.
            error_category:
                Category that the error belongs to.
            reason:
                Why the identified part is invalid.
                This should be a complete sentence.
            start_line_num:
                The line number (within the text) of the first line containing
                the part identified as invalid. This is 1-indexed in line with
                the convention used by many compilers and text editors,
                unlike (probably) every other index in this package,
                hence 'line_num' instead of 'line_index'.
                A value of 0 indicates that this is not applicable.
        """

        super().__init__(error_message)
        self.error_category = error_category
        self.reason = reason
        self.start_line_num = start_line_num

    @classmethod
    def make_short_parse_error(
        cls,
        reason: str,
        *,
        error_category: SledErrorCategory = SledErrorCategory.SYNTAX,
        line: str,
        line_num: int,
        start_index: int,
        end_index: int,
    ) -> Self:
        """
        Factory method for instances involving a single line where the input
        being parsed is invalid.

        Args:
            reason:
                Why the identified part cannot be parsed as valid Sled.
                This should be a complete sentence.
            error_category:
                Category that the error belongs to.
            line:
                The full line (within the text) that contains the part
                identified as invalid. This is expected to be a single line
                and should not contain any line separators.
            line_num:
                Line number (within the text) of the `line` containing
                the part identified as invalid. This is 1-indexed in line with
                the convention used by many compilers and text editors,
                unlike (probably) every other index in this package,
                hence 'line_num' instead of 'line_index'.
            start_index:
                Start index (0-indexed within `line`, inclusive) 
                of the part identified as invalid.
            end_index:
                End index (0-indexed within `line`, exclusive)
                of the part identified as invalid.
        """

        # Validation
        line_length = len(line)
        if not (0 <= start_index < end_index <= line_length + 1):
            raise ValueError(
                "At least one invalid index given when specifying "
                "the location of the invalid Sled input. "
                f"start_index={start_index}, end_index={end_index}, "
                f"line_length={line_length}, line_num={line_num}"
            )
        if DEFAULT_LINE_SEPARATOR in line[:-1]:
            raise ValueError(
                "The line argument should be a single line that does not "
                f"contain any line separators: {repr(line)}"
            )

        # The error message will include the line with the invalid substring,
        # truncated such that the parts before and after the invalid substring
        # each has a length of at most MAX_ERROR_CONTEXT.
        if MAX_ERROR_CONTEXT_LEN < line_length - end_index:
            truncate_index = end_index + MAX_ERROR_CONTEXT_LEN
            line = f"{line[:truncate_index]}{ERROR_ELLIPSIS}"
        initial_strip_index = _len_leading_horizontal_space(line)
        line = line[initial_strip_index:]
        len_before_invalid = start_index - initial_strip_index
        if MAX_ERROR_CONTEXT_LEN < len_before_invalid:
            truncate_index = len_before_invalid - MAX_ERROR_CONTEXT_LEN
            line = f"{ERROR_ELLIPSIS}{line[truncate_index:]}"
            len_before_invalid = (
                MAX_ERROR_CONTEXT_LEN + len(ERROR_ELLIPSIS)
            )

        # Construct the error message
        error_message = (
            f"{reason}\n"
            f"Line {line_num}, from index {start_index} to {end_index}:\n"
            f"{line}\n"
            f"{_SPACE * len_before_invalid}"
            f"{ERROR_POINTER_CHAR * (end_index - start_index)}"
        )

        # Initialize error
        return cls(
            error_message=error_message,
            error_category=error_category,
            reason=reason,
            start_line_num=line_num,
        )

    @classmethod
    def make_duplicate_map_key_error(
        cls,
        data: List[Tuple[Union[str, int], ParseSnapshot]],
        start_line_num: int,
        start_index_within_line: int,
    ) -> Self:
        """
        Finds all duplicate keys in the given `data`
        and constructs a single `SledError` that surfaces all of them.
        """

        groups: DefaultDict[
            Union[str, int], List[ParseSnapshot]
        ] = defaultdict(list)
        for k, snapshot in data:
            groups[k].append(snapshot)

        dup_dict = {
            k: ", ".join(
                f"line {snapshot.line_num} "
                f"index {snapshot.start_index - snapshot.line_start}"
                for snapshot in snapshots
            )
            for k, snapshots in groups.items()
            if len(snapshots) > 1
        }
        dup_str = "\n".join(f"{k}: {reps}" for k, reps in dup_dict.items())

        reason = (
            f"Sled map starting on line {start_line_num} "
            f"at index {start_index_within_line} contains duplicate keys."
        )
        raise cls(
            error_message=f"{reason}\n{dup_str}",
            reason=reason,
            error_category=SledErrorCategory.DUPLICATE_MAP_KEY,
            start_line_num=start_line_num,
        )


def _len_leading_horizontal_space(s: str) -> int:
    for i, c in enumerate(s):
        if c not in HORIZONTAL_SPACE_SET:
            return i
    return len(s)
