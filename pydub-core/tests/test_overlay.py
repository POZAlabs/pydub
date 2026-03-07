import audioop
import struct

import pytest
from pydub_core import overlay_segments as rust_impl

from pydub.overlay import overlay_segments as cython_impl


def _make_8bit(*samples):
    return struct.pack(f"<{len(samples)}b", *samples)


def _make_16bit(*samples):
    return struct.pack(f"<{len(samples)}h", *samples)


def _make_32bit(*samples):
    return struct.pack(f"<{len(samples)}i", *samples)


def _assert_parity(seg1, seg2, sw, position, times, gain=0):
    cython_result = cython_impl(seg1, seg2, sw, position, times, gain)
    rust_result = rust_impl(seg1, seg2, sw, position, times, gain)
    assert rust_result == cython_result


# --- 16-bit parity tests (mirroring test_overlay_segments.py) ---


def test_16bit_no_gain():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)
    seg2 = _make_16bit(100, 200, 300, 400)
    _assert_parity(seg1, seg2, 2, 0, 1)


def test_16bit_positive_gain():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = _make_16bit(100, 200, 300)
    _assert_parity(seg1, seg2, 2, 0, 1, gain=6)


def test_16bit_negative_gain():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = _make_16bit(100, 200, 300)
    _assert_parity(seg1, seg2, 2, 0, 1, gain=-6)


def test_32bit_no_gain():
    seg1 = _make_32bit(100000, 200000, 300000, 400000, 500000, 600000)
    seg2 = _make_32bit(10000, 20000, 30000)
    _assert_parity(seg1, seg2, 4, 0, 1)


def test_32bit_positive_gain():
    seg1 = _make_32bit(100000, 200000, 300000, 400000)
    seg2 = _make_32bit(10000, 20000)
    _assert_parity(seg1, seg2, 4, 0, 1, gain=6)


def test_32bit_negative_gain():
    seg1 = _make_32bit(100000, 200000, 300000, 400000)
    seg2 = _make_32bit(10000, 20000)
    _assert_parity(seg1, seg2, 4, 0, 1, gain=-6)


def test_loop_infinite():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)
    seg2 = _make_16bit(100, 200)
    _assert_parity(seg1, seg2, 2, 0, -1)


def test_fixed_times_1():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = _make_16bit(100, 200)
    _assert_parity(seg1, seg2, 2, 0, 1)


def test_fixed_times_2():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = _make_16bit(100, 200)
    _assert_parity(seg1, seg2, 2, 0, 2)


def test_fixed_times_3():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)
    seg2 = _make_16bit(100, 200)
    _assert_parity(seg1, seg2, 2, 0, 3)


def test_seg2_longer_than_seg1():
    seg1 = _make_16bit(1000, 2000)
    seg2 = _make_16bit(100, 200, 300, 400, 500)
    _assert_parity(seg1, seg2, 2, 0, 1)


def test_position_zero():
    seg1 = _make_16bit(1000, 2000, 3000, 4000)
    seg2 = _make_16bit(100, 200)
    _assert_parity(seg1, seg2, 2, 0, 1)


def test_position_middle():
    seg1 = _make_16bit(1000, 2000, 3000, 4000, 5000, 6000)
    seg2 = _make_16bit(100, 200)
    _assert_parity(seg1, seg2, 2, 4, 1)


def test_position_past_end():
    seg1 = _make_16bit(1000, 2000, 3000)
    seg2 = _make_16bit(100, 200)
    result = rust_impl(seg1, seg2, 2, 100, 1)
    assert result == seg1


def test_saturation_clamp_16bit():
    seg1 = _make_16bit(32000, -32000, 30000, -30000)
    seg2 = _make_16bit(32000, -32000, 32000, -32000)
    _assert_parity(seg1, seg2, 2, 0, 1)


def test_saturation_clamp_32bit():
    seg1 = _make_32bit(2147483000, -2147483000, 2000000000, -2000000000)
    seg2 = _make_32bit(2147483000, -2147483000, 2147483000, -2147483000)
    _assert_parity(seg1, seg2, 4, 0, 1)


def test_saturation_clamp_16bit_with_gain():
    seg1 = _make_16bit(30000, -30000)
    seg2 = _make_16bit(10000, -10000)
    _assert_parity(seg1, seg2, 2, 0, 1, gain=6)


def test_saturation_clamp_32bit_with_gain():
    seg1 = _make_32bit(2000000000, -2000000000)
    seg2 = _make_32bit(1000000000, -1000000000)
    _assert_parity(seg1, seg2, 4, 0, 1, gain=6)


# --- 8-bit (i8) parity tests with audioop reference ---


def _audioop_overlay_8bit(seg1, seg2, position, times, gain=0):
    """Reference using audioop for 8-bit overlay."""
    seg1_len = len(seg1)
    if position >= seg1_len:
        return seg1
    db_factor = 10 ** (gain / 20.0) if gain != 0 else 1.0
    result = bytearray(seg1)
    repeat_to_fill = times < 0
    remaining_times = times
    seg2_len = len(seg2)
    seg1_len_after_pos = seg1_len - position
    current_position = 0
    while (repeat_to_fill or remaining_times > 0) and current_position < seg1_len_after_pos:
        remaining = seg1_len_after_pos - current_position
        chunk_len = min(remaining, seg2_len)
        seg1_slice = bytes(
            result[position + current_position : position + current_position + chunk_len]
        )
        seg2_slice = seg2[:chunk_len]
        if gain != 0:
            seg1_slice = audioop.mul(seg1_slice, 1, db_factor)
        overlaid = audioop.add(seg1_slice, seg2_slice, 1)
        result[position + current_position : position + current_position + chunk_len] = overlaid
        current_position += chunk_len
        if not repeat_to_fill:
            remaining_times -= 1
    return bytes(result)


def test_8bit_no_gain():
    seg1 = _make_8bit(50, 60, 70, 80, 90, 100, 110, 120)
    seg2 = _make_8bit(10, 20, 30, 40)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, 1)
    assert rust_impl(seg1, seg2, 1, 0, 1) == expected


def test_8bit_positive_gain():
    seg1 = _make_8bit(50, 60, 70, 80)
    seg2 = _make_8bit(10, 20)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, 1, gain=6)
    assert rust_impl(seg1, seg2, 1, 0, 1, 6) == expected


def test_8bit_negative_gain():
    seg1 = _make_8bit(50, 60, 70, 80)
    seg2 = _make_8bit(10, 20)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, 1, gain=-6)
    assert rust_impl(seg1, seg2, 1, 0, 1, -6) == expected


def test_8bit_saturation():
    seg1 = _make_8bit(120, -120)
    seg2 = _make_8bit(120, -120)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, 1)
    assert rust_impl(seg1, seg2, 1, 0, 1) == expected


def test_8bit_repeat_to_fill():
    seg1 = _make_8bit(10, 20, 30, 40, 50, 60, 70, 80)
    seg2 = _make_8bit(5, 10)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, -1)
    assert rust_impl(seg1, seg2, 1, 0, -1) == expected


def test_8bit_with_position():
    seg1 = _make_8bit(10, 20, 30, 40, 50, 60)
    seg2 = _make_8bit(5, 10)
    expected = _audioop_overlay_8bit(seg1, seg2, 2, 1)
    assert rust_impl(seg1, seg2, 1, 2, 1) == expected


# --- ValueError tests ---


def test_invalid_sample_width():
    with pytest.raises(ValueError):
        rust_impl(b"\x00\x00\x00", b"\x00\x00\x00", 3, 0, 1)


def test_unaligned_position_16bit():
    with pytest.raises(ValueError):
        rust_impl(b"\x00\x00\x00\x00", b"\x00\x00", 2, 1, 1)


def test_unaligned_seg1_length():
    with pytest.raises(ValueError):
        rust_impl(b"\x00\x00\x00", b"\x00\x00", 2, 0, 1)
