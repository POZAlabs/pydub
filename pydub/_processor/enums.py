import enum
import sys
from collections.abc import Callable
from typing import Any

from ..audio_segment import AudioSegment

if sys.version_info >= (3, 11):
    StrEnum = enum.StrEnum
else:

    class StrEnum(str, enum.Enum):
        ...


class OverlayPolicy(StrEnum):
    FIRST = "first"
    LONGEST = "longest"

    @property
    def sort_key(self) -> Callable[[AudioSegment], Any]:
        keys = {
            OverlayPolicy.FIRST: lambda segment: 0,
            OverlayPolicy.LONGEST: lambda segment: -len(segment),
        }
        return keys[self]
