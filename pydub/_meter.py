from __future__ import annotations

import functools
import tempfile
from collections.abc import Callable
from typing import TYPE_CHECKING, ParamSpec, TypeAlias, TypedDict, TypeVar

if TYPE_CHECKING:
    from .audio_segment import AudioSegment

try:
    import audiometer
except ImportError:
    audiometer = None
    pass


P = ParamSpec("P")
R = TypeVar("R")

dBFS: TypeAlias = float
LUFS: TypeAlias = float


def audiometer_required(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if audiometer is None:
            raise ImportError("`audiometer` is required to measure meter levels")
        return func(*args, **kwargs)

    return wrapper


class Loudness(TypedDict):
    integrated: float
    momentary: list[float]


class AudioLevel(TypedDict, total=False):
    rms: float
    peak: float
    loudness: Loudness


@audiometer_required
def measure_rms(audio_segment: AudioSegment) -> float:
    return round(
        audiometer.measure_rms(
            samples=audio_segment.get_array_of_samples(),
            channels=audio_segment.channels,
            max_amplitude=audio_segment.max_possible_amplitude,
            sample_rate=audio_segment.frame_rate,
        ),
        1,
    )


@audiometer_required
def measure_peak(audio_segment: AudioSegment) -> float:
    return round(
        audiometer.measure_peak(
            samples=audio_segment.get_array_of_samples(),
            channels=audio_segment.channels,
            max_amplitude=audio_segment.max_possible_amplitude,
        ),
        1,
    )


@audiometer_required
def measure_loudness(audio_segment: AudioSegment) -> Loudness:
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        audio_segment.export(
            f.name,
            format="wav",
            codec="pcm_s24le",
        )
        loudness = audiometer.measure_loudness(f.name)

    return Loudness(**loudness)
