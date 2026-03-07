import array

def overlay_segments(
    seg1_data: bytes,
    seg2_data: bytes,
    sample_width: int,
    position: int,
    times: int,
    gain_during_overlay: int = 0,
) -> bytes: ...
def extend_24bit_to_32bit(data: bytes) -> bytes: ...
def measure_rms(
    samples: array.array[int],
    channels: int,
    max_amplitude: float,
    sample_rate: int,
) -> float: ...
def measure_peak(
    samples: array.array[int],
    channels: int,
    max_amplitude: float,
) -> float: ...

class Loudness:
    @property
    def integrated(self) -> float: ...
    @property
    def momentary(self) -> list[float]: ...

def measure_loudness(
    samples: array.array[int],
    channels: int,
    max_amplitude: float,
    sample_rate: int,
) -> Loudness: ...
