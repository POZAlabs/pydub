import gzip


def compress(content: bytes, **kwargs) -> bytes:
    return gzip.compress(content, **kwargs)


def decompress(content: bytes) -> bytes:
    return gzip.decompress(content)
