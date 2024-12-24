import enum
import importlib
from typing import IO, Literal

__all__ = [
    "Compressor",
    "compress",
    "decompress",
]


class Compressor(enum.StrEnum):
    GZIP = enum.auto()
    ZSTD = enum.auto()


def compress(compressor: Compressor, content: bytes, **kwargs) -> bytes:
    module = importlib.import_module(f".{compressor}", package="pydub._compression")
    return module.compress(content, **kwargs)


def decompress(compressor: Compressor, content: bytes) -> bytes:
    module = importlib.import_module(f".{compressor}", package="pydub._compression")
    return module.decompress(content)


def is_compressed(
    stream: IO[bytes],
) -> tuple[Literal[True], Compressor] | tuple[Literal[False], None]:
    for compressor in Compressor.__members__.values():
        try:
            module = importlib.import_module(f".{compressor}", package="pydub._compression")
        except ImportError:
            continue

        if module.is_compressed(stream):
            return True, compressor

    return False, None
