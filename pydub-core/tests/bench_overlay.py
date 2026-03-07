from pathlib import Path

from pydub_core import overlay_segments as rust_impl

from pydub import AudioSegment
from pydub.overlay import overlay_segments as cython_impl

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

seg = AudioSegment.from_file(DATA_DIR / "drums1.wav")
seg1_data = seg.raw_data
seg2_data = AudioSegment.from_file(DATA_DIR / "bass1.wav").raw_data
sample_width = seg.sample_width


def test_bench_overlay_cython(benchmark):
    benchmark(cython_impl, seg1_data, seg2_data, sample_width, 0, 1)


def test_bench_overlay_rust(benchmark):
    benchmark(rust_impl, seg1_data, seg2_data, sample_width, 0, 1)


def test_bench_overlay_with_gain_cython(benchmark):
    benchmark(cython_impl, seg1_data, seg2_data, sample_width, 0, 1, -6)


def test_bench_overlay_with_gain_rust(benchmark):
    benchmark(rust_impl, seg1_data, seg2_data, sample_width, 0, 1, -6)
