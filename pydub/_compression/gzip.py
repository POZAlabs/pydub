import gzip
from typing import IO


def compress(content: bytes, **kwargs) -> bytes:
    return gzip.compress(content, **kwargs)


def decompress(content: bytes) -> bytes:
    return gzip.decompress(content)


def is_compressed(f: IO[bytes]) -> bool:
    f.seek(0)
    f.seek(0)
    result = f.read(2) == b"\x1f\x8b"
    f.seek(0)
    return result
