import audioop
import struct
import time
from pathlib import Path

import pytest

from pydub import AudioSegment, _pydub_core


def _make_8bit(*samples):
    return struct.pack(f"{len(samples)}b", *samples)


def _make_16bit(*samples):
    return struct.pack(f"<{len(samples)}h", *samples)


def _make_32bit(*samples):
    return struct.pack(f"<{len(samples)}i", *samples)


def _reference_mix(segments, sample_width):
    if not segments:
        raise ValueError
    result = segments[0]
    for seg in segments[1:]:
        longer, shorter = (result, seg) if len(result) >= len(seg) else (seg, result)
        mixed = audioop.add(longer[: len(shorter)], shorter, sample_width)
        result = mixed + longer[len(shorter) :]
    return result


# --- Rust layer tests ---


class TestMixSegmentsRust:
    def test_8bit_two_segments(self):
        a = _make_8bit(10, 20, 30)
        b = _make_8bit(5, 10, 15)
        result = _pydub_core.mix_segments([a, b], 1)
        assert result == _reference_mix([a, b], 1)

    def test_16bit_two_segments(self):
        a = _make_16bit(1000, 2000, 3000)
        b = _make_16bit(100, 200, 300)
        result = _pydub_core.mix_segments([a, b], 2)
        assert result == _reference_mix([a, b], 2)

    def test_32bit_two_segments(self):
        a = _make_32bit(100000, 200000, 300000)
        b = _make_32bit(10000, 20000, 30000)
        result = _pydub_core.mix_segments([a, b], 4)
        assert result == _reference_mix([a, b], 4)

    def test_three_or_more_segments(self):
        a = _make_16bit(1000, 2000, 3000)
        b = _make_16bit(100, 200, 300)
        c = _make_16bit(10, 20, 30)
        result = _pydub_core.mix_segments([a, b, c], 2)
        assert result == _reference_mix([a, b, c], 2)

    def test_different_lengths(self):
        a = _make_16bit(1000, 2000, 3000, 4000)
        b = _make_16bit(100, 200)
        result = _pydub_core.mix_segments([a, b], 2)
        expected = _reference_mix([a, b], 2)
        assert result == expected
        assert len(result) == len(a)

    def test_different_lengths_three_segments(self):
        a = _make_16bit(1000, 2000)
        b = _make_16bit(100, 200, 300, 400)
        c = _make_16bit(10, 20, 30)
        result = _pydub_core.mix_segments([a, b, c], 2)
        expected = _reference_mix([a, b, c], 2)
        assert result == expected
        assert len(result) == len(b)

    def test_saturation_clamp_8bit(self):
        a = _make_8bit(120, -120)
        b = _make_8bit(120, -120)
        result = _pydub_core.mix_segments([a, b], 1)
        assert result == _reference_mix([a, b], 1)

    def test_saturation_clamp_16bit(self):
        a = _make_16bit(32000, -32000)
        b = _make_16bit(32000, -32000)
        result = _pydub_core.mix_segments([a, b], 2)
        assert result == _reference_mix([a, b], 2)

    def test_saturation_clamp_32bit(self):
        a = _make_32bit(2147483000, -2147483000)
        b = _make_32bit(2147483000, -2147483000)
        result = _pydub_core.mix_segments([a, b], 4)
        assert result == _reference_mix([a, b], 4)

    def test_empty_list_raise_error(self):
        with pytest.raises(ValueError):
            _pydub_core.mix_segments([], 2)

    def test_invalid_sample_width_raise_error(self):
        a = _make_16bit(1000)
        with pytest.raises(ValueError):
            _pydub_core.mix_segments([a], 3)


# --- AudioSegment layer tests ---


DATA_DIR = Path(__file__).parent.parent / "data"


class TestAudioSegmentMix:
    def test_two_segments_match_overlay(self):
        a = AudioSegment.silent(duration=100)
        b = AudioSegment.silent(duration=100)
        mixed = AudioSegment.mix(a, b)
        overlaid = a.overlay(b, position=0)
        assert mixed.raw_data == overlaid.raw_data

    def test_single_segment_return_same_object(self):
        a = AudioSegment.silent(duration=100)
        result = AudioSegment.mix(a)
        assert result is a

    def test_empty_raise_error(self):
        with pytest.raises(ValueError):
            AudioSegment.mix()

    def test_different_lengths(self):
        a = AudioSegment.silent(duration=200)
        b = AudioSegment.silent(duration=100)
        result = AudioSegment.mix(a, b)
        assert len(result) == len(a)

    def test_mix_all_wav_files(self):
        wav_files = sorted(DATA_DIR.glob("*.wav"))
        segs = [AudioSegment.from_file(f) for f in wav_files]
        result = AudioSegment.mix(*segs)
        expected_len = max(len(s) for s in segs)
        assert len(result) == expected_len


# --- Performance benchmark ---


def test_mix_performance():
    wav_files = sorted(DATA_DIR.glob("*.wav"))
    segs = [AudioSegment.from_file(f) for f in wav_files]
    n_runs = 5

    # overlay chaining
    times_overlay = []
    for _ in range(n_runs):
        start = time.perf_counter()
        result = segs[0]
        for seg in segs[1:]:
            result = result.overlay(seg, position=0)
        times_overlay.append(time.perf_counter() - start)

    # mix
    times_mix = []
    for _ in range(n_runs):
        start = time.perf_counter()
        result = AudioSegment.mix(*segs)
        times_mix.append(time.perf_counter() - start)

    avg_overlay = sum(times_overlay) / n_runs
    avg_mix = sum(times_mix) / n_runs
    print(f"\noverlay chaining: {avg_overlay:.4f}s (avg of {n_runs} runs)")
    print(f"mix:              {avg_mix:.4f}s (avg of {n_runs} runs)")
    print(f"speedup:          {avg_overlay / avg_mix:.2f}x")
