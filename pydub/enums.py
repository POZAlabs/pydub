import enum
import sys

if sys.version_info >= (3, 11):
    StrEnum = enum.StrEnum
else:

    class StrEnum(str, enum.Enum):
        ...


class OverlayPolicy(StrEnum):
    FIRST = "first"
    LONGEST = "longest"
