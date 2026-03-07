import pytest
from pydub_core import extend_24bit_to_32bit as rust_impl

from pydub.sample import extend_24bit_to_32bit as cython_impl


def _assert_parity(data):
    assert rust_impl(data) == cython_impl(data)


def test_3_bytes():
    _assert_parity(b"\x01\x02\x03")


def test_6_bytes():
    _assert_parity(b"\x01\x02\x03\x04\x05\x06")


def test_9_bytes():
    _assert_parity(b"\x01\x02\x03\x04\x05\x06\x07\x08\x09")


def test_300_bytes():
    data = bytes(range(256)) + bytes(range(44))
    assert len(data) == 300
    _assert_parity(data)


def test_positive_sample_sign_extension():
    data = b"\x01\x02\x03"
    result = rust_impl(data)
    assert result[0] == 0x00
    assert result[1:4] == data


def test_negative_sample_sign_extension():
    data = b"\x01\x02\x83"
    result = rust_impl(data)
    assert result[0] == 0xFF
    assert result[1:4] == data


def test_zero_sample():
    data = b"\x00\x00\x00"
    result = rust_impl(data)
    assert result == b"\x00\x00\x00\x00"


def test_invalid_length_not_multiple_of_3():
    with pytest.raises(ValueError):
        rust_impl(b"\x01\x02")


def test_invalid_length_1():
    with pytest.raises(ValueError):
        rust_impl(b"\x01")


def test_invalid_length_4():
    with pytest.raises(ValueError):
        rust_impl(b"\x01\x02\x03\x04")


def test_empty_input():
    assert rust_impl(b"") == b""
