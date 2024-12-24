from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING, TypedDict

from .utils import create_extra_required

if TYPE_CHECKING:
    from .audio_segment import AudioSegment

try:
    import audiometer
except ImportError:
    audiometer = None
    pass


audiometer_required = create_extra_required(
    module="audiometer",
    message="`audiometer` is required to measure meter levels",
)


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
