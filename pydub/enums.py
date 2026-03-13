from __future__ import annotations

import enum


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
        _ARRAY_TYPES = {1: "b", 2: "h", 4: "i"}
        if self.value not in _ARRAY_TYPES:
            raise ValueError(f"Array type is not available for {self.name} (24-bit)")
        return _ARRAY_TYPES[self.value]

    @property
    def value_range(self) -> tuple[int, int]:
        if self == SampleWidth.PCM24:
            raise ValueError(f"Value range is not available for {self.name} (24-bit)")
        bits = self.bit_depth
        return -(1 << (bits - 1)), (1 << (bits - 1)) - 1
