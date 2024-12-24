import importlib
from typing import Literal, TypeAlias

__all__ = [
    "Compressor",
    "compress",
    "decompress",
]

Compressor: TypeAlias = Literal["gzip", "zstd"]


def compress(compressor: Compressor, content: bytes, **kwargs) -> bytes:
    module = importlib.import_module(f".{compressor}", package="pydub.compression")
    return module.compress(content, **kwargs)


def decompress(compressor: Compressor, content: bytes) -> bytes:
    module = importlib.import_module(f".{compressor}", package="pydub.compression")
    return module.decompress(content)
