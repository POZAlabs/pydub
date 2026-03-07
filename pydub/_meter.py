from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from ._pydub_core import measure_loudness as _measure_loudness
from ._pydub_core import measure_peak as _measure_peak
from ._pydub_core import measure_rms as _measure_rms

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
        _measure_rms(
            samples=audio_segment.get_array_of_samples(),
            channels=audio_segment.channels,
            max_amplitude=audio_segment.max_possible_amplitude,
            sample_rate=audio_segment.frame_rate,
        ),
        1,
    )


def measure_peak(audio_segment: AudioSegment) -> float:
    return round(
        _measure_peak(
            samples=audio_segment.get_array_of_samples(),
            channels=audio_segment.channels,
            max_amplitude=audio_segment.max_possible_amplitude,
        ),
        1,
    )


def measure_loudness(audio_segment: AudioSegment) -> Loudness:
    result = _measure_loudness(
        samples=audio_segment.get_array_of_samples(),
        channels=audio_segment.channels,
        max_amplitude=audio_segment.max_possible_amplitude,
        sample_rate=audio_segment.frame_rate,
    )
    return Loudness(
        integrated=round(result.integrated, 1),
        momentary=[round(m, 1) for m in result.momentary],
    )
