from pydub.utils import create_extra_required

try:
    import zstandard
except ImportError:
    zstandard = None


zstd_required = create_extra_required(
    module=zstandard,
    message="`zstandard` is required to use zstd compression",
)


def compress(content: bytes, **kwargs) -> bytes:
    return zstandard.compress(content, **kwargs)


def decompress(content: bytes) -> bytes:
    return zstandard.decompress(content)
