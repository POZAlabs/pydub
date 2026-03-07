import array

from pydub import _pydub_core


def test_rms_silence():
    samples = array.array("i", [0] * 44100)
    result = _pydub_core.measure_rms(
        samples, channels=1, max_amplitude=2147483648.0, sample_rate=44100
    )
    assert result == float("-inf")


def test_peak_silence():
    samples = array.array("i", [0] * 44100)
    result = _pydub_core.measure_peak(samples, channels=1, max_amplitude=2147483648.0)
    assert result == float("-inf")
