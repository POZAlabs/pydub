import io
from unittest.mock import patch

from pydub._compression import Compressor, is_compressed


def test_is_compressed_return_false_when_optional_dependency_not_installed():
    non_compressed_stream = io.BytesIO(b"\x00\x00\x00\x00")

    with patch.dict("sys.modules", {"zstandard": None}):
        result, compressor = is_compressed(non_compressed_stream)

    assert result is False
    assert compressor is None


def test_is_compressed_detect_gzip():
    gzip_stream = io.BytesIO(b"\x1f\x8b" + b"\x00" * 10)

    result, compressor = is_compressed(gzip_stream)

    assert result is True
    assert compressor == Compressor.GZIP


def test_is_compressed_return_false_for_non_compressed_stream():
    stream = io.BytesIO(b"\x00\x00\x00\x00")

    result, compressor = is_compressed(stream)

    assert result is False
    assert compressor is None
