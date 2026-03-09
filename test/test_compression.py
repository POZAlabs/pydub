import io

from pydub._compression import Compressor, is_compressed


def test_is_compressed_detect_gzip():
    gzip_stream = io.BytesIO(b"\x1f\x8b" + b"\x00" * 10)

    result, compressor = is_compressed(gzip_stream)

    assert result is True
    assert compressor == Compressor.GZIP


def test_is_compressed_detect_zstd():
    zstd_stream = io.BytesIO(b"\x28\xb5\x2f\xfd" + b"\x00" * 10)

    result, compressor = is_compressed(zstd_stream)

    assert result is True
    assert compressor == Compressor.ZSTD


def test_is_compressed_return_false_for_non_compressed_stream():
    stream = io.BytesIO(b"\x00\x00\x00\x00")

    result, compressor = is_compressed(stream)

    assert result is False
    assert compressor is None
