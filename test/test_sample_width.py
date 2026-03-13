import pytest

from pydub.enums import SampleWidth


class TestFromBitDepth:
    @pytest.mark.parametrize(
        "bits, expected",
        [
            (8, SampleWidth.PCM8),
            (16, SampleWidth.PCM16),
            (24, SampleWidth.PCM24),
            (32, SampleWidth.PCM32),
        ],
    )
    def test_convert_bit_depth_to_sample_width(self, bits, expected):
        assert SampleWidth.from_bit_depth(bits) == expected


class TestBitDepth:
    @pytest.mark.parametrize(
        "sw, expected",
        [
            (SampleWidth.PCM8, 8),
            (SampleWidth.PCM16, 16),
            (SampleWidth.PCM24, 24),
            (SampleWidth.PCM32, 32),
        ],
    )
    def test_return_bit_depth(self, sw, expected):
        assert sw.bit_depth == expected


class TestArrayType:
    @pytest.mark.parametrize(
        "sw, expected",
        [(SampleWidth.PCM8, "b"), (SampleWidth.PCM16, "h"), (SampleWidth.PCM32, "i")],
    )
    def test_return_array_type(self, sw, expected):
        assert sw.array_type == expected

    def test_raise_for_pcm24(self):
        with pytest.raises(ValueError):
            SampleWidth.PCM24.array_type


class TestValueRange:
    @pytest.mark.parametrize(
        "sw, expected",
        [
            (SampleWidth.PCM8, (-128, 127)),
            (SampleWidth.PCM16, (-32768, 32767)),
            (SampleWidth.PCM32, (-2147483648, 2147483647)),
        ],
    )
    def test_return_value_range(self, sw, expected):
        assert sw.value_range == expected

    def test_raise_for_pcm24(self):
        with pytest.raises(ValueError):
            SampleWidth.PCM24.value_range


class TestIntEnumCompatibility:
    def test_is_instance_of_int(self):
        assert isinstance(SampleWidth.PCM16, int)

    def test_equal_to_int_literal(self):
        assert SampleWidth.PCM16 == 2
