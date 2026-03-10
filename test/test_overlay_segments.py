import audioop

from pydub import _pydub_core
from test.helper import make_16bit, make_32bit


def _reference_overlay_segments(
    seg1_data, seg2_data, sample_width, position, times, gain_during_overlay=0
):
    """Reference implementation using audioop (pre-optimization logic)."""
    seg1_len = len(seg1_data)
    seg2_len = len(seg2_data)
    remaining_times = times
    db_factor = 1.0

    if position >= seg1_len:
        return seg1_data

    apply_gain = gain_during_overlay != 0
    if apply_gain:
        db_factor = 10 ** (gain_during_overlay / 20.0)

    result_before = seg1_data[:position]

    seg1_data = seg1_data[position:]
    seg1_len = len(seg1_data)
    current_position = 0
    overlaid_slices = []
    while True:
        if remaining_times == 0:
            break
        if current_position >= seg1_len:
            break

        remaining = max(seg1_len - current_position, 0)
        current_seg2_len = remaining if remaining < seg2_len else seg2_len

        seg1_slice = seg1_data[current_position : current_position + current_seg2_len]
        seg2_slice = seg2_data[:current_seg2_len]

        if apply_gain:
            seg1_slice = audioop.mul(seg1_slice, sample_width, db_factor)

        overlaid_slice = audioop.add(seg1_slice, seg2_slice, sample_width)
        overlaid_slices.append(overlaid_slice)

        current_position += current_seg2_len

        if remaining_times > 0:
            remaining_times -= 1

    return result_before + b"".join(overlaid_slices) + seg1_data[current_position:]


def _assert_match(seg1, seg2, sw, position, times, gain=0):
    result = _pydub_core.overlay_segments(seg1, seg2, sw, position, times, gain)
    expected = _reference_overlay_segments(seg1, seg2, sw, position, times, gain)
    assert result == expected


def test_16bit_no_gain():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)
    seg2 = make_16bit(100, 200, 300, 400)
    _assert_match(seg1, seg2, 2, 0, 1)


def test_16bit_positive_gain():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = make_16bit(100, 200, 300)
    _assert_match(seg1, seg2, 2, 0, 1, gain=6)


def test_16bit_negative_gain():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = make_16bit(100, 200, 300)
    _assert_match(seg1, seg2, 2, 0, 1, gain=-6)


def test_32bit_no_gain():
    seg1 = make_32bit(100000, 200000, 300000, 400000, 500000, 600000)
    seg2 = make_32bit(10000, 20000, 30000)
    _assert_match(seg1, seg2, 4, 0, 1)


def test_32bit_positive_gain():
    seg1 = make_32bit(100000, 200000, 300000, 400000)
    seg2 = make_32bit(10000, 20000)
    _assert_match(seg1, seg2, 4, 0, 1, gain=6)


def test_32bit_negative_gain():
    seg1 = make_32bit(100000, 200000, 300000, 400000)
    seg2 = make_32bit(10000, 20000)
    _assert_match(seg1, seg2, 4, 0, 1, gain=-6)


def test_loop_infinite():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)
    seg2 = make_16bit(100, 200)
    _assert_match(seg1, seg2, 2, 0, -1)


def test_fixed_times_1():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = make_16bit(100, 200)
    _assert_match(seg1, seg2, 2, 0, 1)


def test_fixed_times_2():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = make_16bit(100, 200)
    _assert_match(seg1, seg2, 2, 0, 2)


def test_fixed_times_3():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)
    seg2 = make_16bit(100, 200)
    _assert_match(seg1, seg2, 2, 0, 3)


def test_seg2_longer_than_seg1():
    seg1 = make_16bit(1000, 2000)
    seg2 = make_16bit(100, 200, 300, 400, 500)
    _assert_match(seg1, seg2, 2, 0, 1)


def test_position_zero():
    seg1 = make_16bit(1000, 2000, 3000, 4000)
    seg2 = make_16bit(100, 200)
    _assert_match(seg1, seg2, 2, 0, 1)


def test_position_middle():
    seg1 = make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = make_16bit(100, 200)
    _assert_match(seg1, seg2, 2, 4, 1)


def test_position_past_end():
    seg1 = make_16bit(1000, 2000, 3000)
    seg2 = make_16bit(100, 200)
    result = _pydub_core.overlay_segments(seg1, seg2, 2, 100, 1)
    assert result == seg1


def test_saturation_clamp_16bit():
    seg1 = make_16bit(32000, -32000, 30000, -30000)
    seg2 = make_16bit(32000, -32000, 32000, -32000)
    _assert_match(seg1, seg2, 2, 0, 1)


def test_saturation_clamp_32bit():
    seg1 = make_32bit(2147483000, -2147483000, 2000000000, -2000000000)
    seg2 = make_32bit(2147483000, -2147483000, 2147483000, -2147483000)
    _assert_match(seg1, seg2, 4, 0, 1)


def test_saturation_clamp_16bit_with_gain():
    seg1 = make_16bit(30000, -30000)
    seg2 = make_16bit(10000, -10000)
    _assert_match(seg1, seg2, 2, 0, 1, gain=6)


def test_saturation_clamp_32bit_with_gain():
    seg1 = make_32bit(2000000000, -2000000000)
    seg2 = make_32bit(1000000000, -1000000000)
    _assert_match(seg1, seg2, 4, 0, 1, gain=6)
