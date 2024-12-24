from typing import IO

from pydub.utils import create_extra_required

try:
    import zstandard
except ImportError:
    zstandard = None


zstd_required = create_extra_required(
    module=zstandard,
    message="`zstandard` is required to use zstd compression",
)


@zstd_required
def compress(content: bytes, **kwargs) -> bytes:
    return zstandard.compress(content, **kwargs)


@zstd_required
def decompress(content: bytes) -> bytes:
    return zstandard.decompress(content)


@zstd_required
def is_compressed(f: IO[bytes]) -> bool:
    f.seek(0)
    result = f.read(4) == b"(\xb5/\xfd"
    f.seek(0)
    return result
