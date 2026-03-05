import io
from unittest.mock import patch

from pydub._compression import Compressor, is_compressed


class TestIsCompressed:
    def test_return_false_when_optional_dependency_not_installed(self):
        non_compressed_stream = io.BytesIO(b"\x00\x00\x00\x00")

        with patch.dict("sys.modules", {"zstandard": None}):
            result, compressor = is_compressed(non_compressed_stream)

        assert result is False
        assert compressor is None

    def test_detect_gzip(self):
        gzip_stream = io.BytesIO(b"\x1f\x8b" + b"\x00" * 10)

        result, compressor = is_compressed(gzip_stream)

        assert result is True
        assert compressor == Compressor.GZIP

    def test_return_false_for_non_compressed_stream(self):
        stream = io.BytesIO(b"\x00\x00\x00\x00")

        result, compressor = is_compressed(stream)

        assert result is False
        assert compressor is None
