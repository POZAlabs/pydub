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
            samples=audio_segment.get_array_of_samples(),
            channels=audio_segment.channels,
            max_amplitude=audio_segment.max_possible_amplitude,
            sample_rate=audio_segment.frame_rate,
        ),
        1,
    )


def measure_peak(audio_segment: AudioSegment) -> float:
    return round(
        _pydub_core.measure_peak(
            samples=audio_segment.get_array_of_samples(),
            channels=audio_segment.channels,
            max_amplitude=audio_segment.max_possible_amplitude,
        ),
        1,
    )


def measure_loudness(audio_segment: AudioSegment) -> Loudness:
    result = _pydub_core.measure_loudness(
        samples=audio_segment.get_array_of_samples(),
        channels=audio_segment.channels,
        max_amplitude=audio_segment.max_possible_amplitude,
        sample_rate=audio_segment.frame_rate,
    )
    return Loudness(
        integrated=round(result.integrated, 1),
        momentary=[round(m, 1) for m in result.momentary],
    )
