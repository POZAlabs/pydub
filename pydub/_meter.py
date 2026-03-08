from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from . import _pydub_core

if TYPE_CHECKING:
    from .audio_segment import AudioSegment


class Loudness(TypedDict):
    integrated: float
    momentary: list[float]


class AudioLevel(TypedDict, total=False):
    rms: float
    peak: float
    loudness: Loudness


def measure_rms(audio_segment: AudioSegment) -> float:
    return round(
        _pydub_core.measure_rms(
            data=audio_segment.raw_data,
            sample_width=audio_segment.sample_width,
            channels=audio_segment.channels,
            sample_rate=audio_segment.frame_rate,
        ),
        1,
    )


def measure_peak(audio_segment: AudioSegment) -> float:
    return round(
        _pydub_core.measure_peak(
            data=audio_segment.raw_data,
            sample_width=audio_segment.sample_width,
            channels=audio_segment.channels,
        ),
        1,
    )


def measure_loudness(audio_segment: AudioSegment) -> Loudness:
    result = _pydub_core.measure_loudness(
        data=audio_segment.raw_data,
        sample_width=audio_segment.sample_width,
        channels=audio_segment.channels,
        sample_rate=audio_segment.frame_rate,
    )
    return Loudness(
        integrated=round(result.integrated, 1),
        momentary=[round(m, 1) for m in result.momentary],
    )
