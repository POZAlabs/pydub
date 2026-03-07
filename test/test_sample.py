import pytest

from pydub._pydub_core import extend_24bit_to_32bit


def test_3_bytes():
    data = b"\x01\x02\x03"
    result = extend_24bit_to_32bit(data)
    assert len(result) == 4


def test_6_bytes():
    data = b"\x01\x02\x03\x04\x05\x06"
    result = extend_24bit_to_32bit(data)
    assert len(result) == 8


def test_300_bytes():
    data = bytes(range(256)) + bytes(range(44))
    assert len(data) == 300
    result = extend_24bit_to_32bit(data)
    assert len(result) == 400


def test_positive_sample_sign_extension():
    data = b"\x01\x02\x03"
    result = extend_24bit_to_32bit(data)
    assert result[0] == 0x00
    assert result[1:4] == data


def test_negative_sample_sign_extension():
    data = b"\x01\x02\x83"
    result = extend_24bit_to_32bit(data)
    assert result[0] == 0xFF
    assert result[1:4] == data


def test_zero_sample():
    data = b"\x00\x00\x00"
    result = extend_24bit_to_32bit(data)
    assert result == b"\x00\x00\x00\x00"


def test_invalid_length_not_multiple_of_3():
    with pytest.raises(ValueError):
        extend_24bit_to_32bit(b"\x01\x02")


def test_invalid_length_1():
    with pytest.raises(ValueError):
        extend_24bit_to_32bit(b"\x01")


def test_invalid_length_4():
    with pytest.raises(ValueError):
        extend_24bit_to_32bit(b"\x01\x02\x03\x04")


def test_empty_input():
    assert extend_24bit_to_32bit(b"") == b""
