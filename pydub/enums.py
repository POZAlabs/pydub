from __future__ import annotations

import enum

_ARRAY_TYPES = {1: "b", 2: "h", 4: "i"}


class SampleWidth(enum.IntEnum):
    PCM8 = 1
    PCM16 = 2
    PCM24 = 3
    PCM32 = 4

    @classmethod
    def from_bit_depth(cls, bits: int) -> SampleWidth:
        return cls(bits // 8)

    @property
    def bit_depth(self) -> int:
        return self.value * 8

    @property
    def array_type(self) -> str:
        if self.value not in _ARRAY_TYPES:
            raise ValueError("'array_type' is not available for 24-bit sample width")
        return _ARRAY_TYPES[self.value]

    @property
    def value_range(self) -> tuple[int, int]:
        if self == SampleWidth.PCM24:
            raise ValueError("'value_range' is not available for 24-bit sample width")
        bits = self.bit_depth
        return -(1 << (bits - 1)), (1 << (bits - 1)) - 1
