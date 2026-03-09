from typing import IO

try:
    from compression.zstd import compress, decompress
except ImportError:
    from backports.zstd import compress, decompress

__all__ = ["compress", "decompress", "is_compressed"]


def is_compressed(f: IO[bytes]) -> bool:
    f.seek(0)
    result = f.read(4) == b"(\xb5/\xfd"
    f.seek(0)
    return result
