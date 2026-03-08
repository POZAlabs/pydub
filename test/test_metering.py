from pydub import _pydub_core


def test_rms_silence():
    data = b"\x00" * (44100 * 4)
    result = _pydub_core.measure_rms(data, sample_width=4, channels=1, sample_rate=44100)
    assert result == float("-inf")


def test_peak_silence():
    data = b"\x00" * (44100 * 4)
    result = _pydub_core.measure_peak(data, sample_width=4, channels=1)
    assert result == float("-inf")
