from pathlib import Path

from pydub_core import extend_24bit_to_32bit as rust_impl

from pydub import AudioSegment
from pydub.sample import extend_24bit_to_32bit as cython_impl

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

seg = AudioSegment.from_file(DATA_DIR / "drums1.wav")
# Simulate 24-bit data by trimming each 4-byte sample to 3 bytes
raw = seg.raw_data
sample_count = len(raw) // 4
data_24bit = b"".join(raw[i * 4 + 1 : i * 4 + 4] for i in range(sample_count))


def test_bench_extend_24bit_cython(benchmark):
    benchmark(cython_impl, data_24bit)


def test_bench_extend_24bit_rust(benchmark):
    benchmark(rust_impl, data_24bit)
