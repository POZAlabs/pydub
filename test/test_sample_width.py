import pytest

from pydub.enums import SampleWidth


@pytest.mark.parametrize(
    "bits, expected",
    [
        (8, SampleWidth.PCM8),
        (16, SampleWidth.PCM16),
        (24, SampleWidth.PCM24),
        (32, SampleWidth.PCM32),
    ],
)
def test_from_bit_depth_resolve_bit_depth_to_matching_member(bits, expected):
    assert SampleWidth.from_bit_depth(bits) == expected


@pytest.mark.parametrize(
    "sw, expected",
    [
        (SampleWidth.PCM8, 8),
        (SampleWidth.PCM16, 16),
        (SampleWidth.PCM24, 24),
        (SampleWidth.PCM32, 32),
    ],
)
def test_bit_depth_reverse_byte_to_bit_conversion(sw, expected):
    assert sw.bit_depth == expected


@pytest.mark.parametrize(
    "sw, expected",
    [(SampleWidth.PCM8, "b"), (SampleWidth.PCM16, "h"), (SampleWidth.PCM32, "i")],
)
def test_array_type_map_to_python_array_typecode(sw, expected):
    assert sw.array_type == expected


def test_array_type_reject_pcm24_without_array_representation():
    with pytest.raises(ValueError):
        SampleWidth.PCM24.array_type


@pytest.mark.parametrize(
    "sw, expected",
    [
        (SampleWidth.PCM8, (-128, 127)),
        (SampleWidth.PCM16, (-32768, 32767)),
        (SampleWidth.PCM32, (-2147483648, 2147483647)),
    ],
)
def test_value_range_return_signed_integer_bounds(sw, expected):
    assert sw.value_range == expected


def test_value_range_reject_pcm24_without_array_representation():
    with pytest.raises(ValueError):
        SampleWidth.PCM24.value_range
