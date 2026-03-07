import audioop
import struct

import pytest

from pydub import _pydub_core


def _make_8bit(*samples):
    return struct.pack(f"<{len(samples)}b", *samples)


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
    assert _pydub_core.overlay_segments(seg1, seg2, 1, 0, 1) == expected


def test_8bit_positive_gain():
    seg1 = _make_8bit(50, 60, 70, 80)
    seg2 = _make_8bit(10, 20)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, 1, gain=6)
    assert _pydub_core.overlay_segments(seg1, seg2, 1, 0, 1, 6) == expected


def test_8bit_negative_gain():
    seg1 = _make_8bit(50, 60, 70, 80)
    seg2 = _make_8bit(10, 20)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, 1, gain=-6)
    assert _pydub_core.overlay_segments(seg1, seg2, 1, 0, 1, -6) == expected


def test_8bit_saturation():
    seg1 = _make_8bit(120, -120)
    seg2 = _make_8bit(120, -120)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, 1)
    assert _pydub_core.overlay_segments(seg1, seg2, 1, 0, 1) == expected


def test_8bit_repeat_to_fill():
    seg1 = _make_8bit(10, 20, 30, 40, 50, 60, 70, 80)
    seg2 = _make_8bit(5, 10)
    expected = _audioop_overlay_8bit(seg1, seg2, 0, -1)
    assert _pydub_core.overlay_segments(seg1, seg2, 1, 0, -1) == expected


def test_8bit_with_position():
    seg1 = _make_8bit(10, 20, 30, 40, 50, 60)
    seg2 = _make_8bit(5, 10)
    expected = _audioop_overlay_8bit(seg1, seg2, 2, 1)
    assert _pydub_core.overlay_segments(seg1, seg2, 1, 2, 1) == expected


# --- ValueError tests ---


def test_invalid_sample_width():
    with pytest.raises(ValueError):
        _pydub_core.overlay_segments(b"\x00\x00\x00", b"\x00\x00\x00", 3, 0, 1)


def test_unaligned_position_16bit():
    with pytest.raises(ValueError):
        _pydub_core.overlay_segments(b"\x00\x00\x00\x00", b"\x00\x00", 2, 1, 1)


def test_unaligned_seg1_length():
    with pytest.raises(ValueError):
        _pydub_core.overlay_segments(b"\x00\x00\x00", b"\x00\x00", 2, 0, 1)
