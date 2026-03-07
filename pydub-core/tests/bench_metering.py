from pathlib import Path

import audiometer
import pydub_core

from pydub import AudioSegment

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

seg = AudioSegment.from_file(DATA_DIR / "drums1.wav")
samples = seg.get_array_of_samples()
channels = seg.channels
max_amplitude = seg.max_possible_amplitude
sample_rate = seg.frame_rate


def test_bench_rms_audiometer(benchmark):
    benchmark(audiometer.measure_rms, samples, channels, max_amplitude, sample_rate)


def test_bench_rms_rust(benchmark):
    benchmark(pydub_core.measure_rms, samples, channels, max_amplitude, sample_rate)


def test_bench_peak_audiometer(benchmark):
    benchmark(audiometer.measure_peak, samples, channels, max_amplitude)


def test_bench_peak_rust(benchmark):
    benchmark(pydub_core.measure_peak, samples, channels, max_amplitude)


def test_bench_loudness_audiometer(benchmark):
    benchmark(audiometer.measure_loudness, samples, channels, max_amplitude, sample_rate)


def test_bench_loudness_rust(benchmark):
    benchmark(pydub_core.measure_loudness, samples, channels, max_amplitude, sample_rate)
