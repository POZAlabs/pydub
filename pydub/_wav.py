from __future__ import annotations

import struct
from dataclasses import dataclass

from .exceptions import CouldntDecodeError


@dataclass(frozen=True, slots=True)
class SubChunk:
    id: bytes
    position: int
    size: int


@dataclass(frozen=True, slots=True)
class AudioData:
    audio_format: int
    channels: int
    sample_rate: int
    bits_per_sample: int
    raw_data: bytes


def extract_headers(data: bytes) -> list[SubChunk]:
    pos = 12  # The size of the RIFF chunk descriptor
    subchunks: list[SubChunk] = []
    while pos + 8 <= len(data) and len(subchunks) < 10:
        subchunk_id = data[pos : pos + 4]
        subchunk_size = struct.unpack_from("<I", data[pos + 4 : pos + 8])[0]
        subchunks.append(SubChunk(subchunk_id, pos, subchunk_size))
        if subchunk_id == b"data":
            break
        pos += subchunk_size + 8

    return subchunks


def read_audio(data: bytes, headers: list[SubChunk] | None = None) -> AudioData:
    if not headers:
        headers = extract_headers(data)

    fmt = [x for x in headers if x.id == b"fmt "]
    if not fmt or fmt[0].size < 16:
        raise CouldntDecodeError("Could not find fmt header in wav data")
    fmt = fmt[0]
    pos = fmt.position + 8
    audio_format = struct.unpack_from("<H", data[pos : pos + 2])[0]
    if audio_format != 1 and audio_format != 0xFFFE:
        raise CouldntDecodeError(f"Unknown audio format 0x{audio_format:X} in wav data")

    channels = struct.unpack_from("<H", data[pos + 2 : pos + 4])[0]
    sample_rate = struct.unpack_from("<I", data[pos + 4 : pos + 8])[0]
    bits_per_sample = struct.unpack_from("<H", data[pos + 14 : pos + 16])[0]

    data_hdr = headers[-1]
    if data_hdr.id != b"data":
        raise CouldntDecodeError("Could not find data header in wav data")

    pos = data_hdr.position + 8
    return AudioData(
        audio_format, channels, sample_rate, bits_per_sample, data[pos : pos + data_hdr.size]
    )


def fix_headers(data: bytes) -> bytes:
    headers = extract_headers(data)
    if not headers or headers[-1].id != b"data":
        return data

    if len(data) > 2**32:
        raise CouldntDecodeError("Unable to process >4GB files")

    result = bytearray(data)

    result[4:8] = struct.pack("<I", len(result) - 8)

    pos = headers[-1].position
    result[pos + 4 : pos + 8] = struct.pack("<I", len(result) - pos - 8)

    return bytes(result)
