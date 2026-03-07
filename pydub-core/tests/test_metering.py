import array

import audiometer
import pydub_core


def _make_samples(seg):
    return seg.get_array_of_samples()


def _get_params(seg):
    return {
        "channels": seg.channels,
        "max_amplitude": seg.max_possible_amplitude,
        "sample_rate": seg.frame_rate,
    }


def test_rms_parity(drums1):
    samples = _make_samples(drums1)
    params = _get_params(drums1)
    expected = audiometer.measure_rms(samples, **params)
    result = pydub_core.measure_rms(samples, **params)
    assert result == expected


def test_peak_parity(drums1):
    samples = _make_samples(drums1)
    params = _get_params(drums1)
    del params["sample_rate"]
    expected = audiometer.measure_peak(samples, **params)
    result = pydub_core.measure_peak(samples, **params)
    assert result == expected


def test_loudness_parity(drums1):
    samples = _make_samples(drums1)
    params = _get_params(drums1)
    expected = audiometer.measure_loudness(samples, **params)
    result = pydub_core.measure_loudness(samples, **params)
    # audiometer 0.17.0 returns dict, pydub_core returns pyclass
    exp_integrated = expected["integrated"] if isinstance(expected, dict) else expected.integrated
    exp_momentary = expected["momentary"] if isinstance(expected, dict) else expected.momentary
    assert result.integrated == exp_integrated
    assert list(result.momentary) == list(exp_momentary)


def test_rms_silence():
    samples = array.array("i", [0] * 44100)
    result = pydub_core.measure_rms(
        samples, channels=1, max_amplitude=2147483648.0, sample_rate=44100
    )
    assert result == float("-inf")


def test_peak_silence():
    samples = array.array("i", [0] * 44100)
    result = pydub_core.measure_peak(samples, channels=1, max_amplitude=2147483648.0)
    assert result == float("-inf")


def test_rms_parity_bass(bass1):
    samples = _make_samples(bass1)
    params = _get_params(bass1)
    expected = audiometer.measure_rms(samples, **params)
    result = pydub_core.measure_rms(samples, **params)
    assert result == expected


def test_peak_parity_bass(bass1):
    samples = _make_samples(bass1)
    params = _get_params(bass1)
    del params["sample_rate"]
    expected = audiometer.measure_peak(samples, **params)
    result = pydub_core.measure_peak(samples, **params)
    assert result == expected


def test_loudness_parity_bass(bass1):
    samples = _make_samples(bass1)
    params = _get_params(bass1)
    expected = audiometer.measure_loudness(samples, **params)
    result = pydub_core.measure_loudness(samples, **params)
    exp_integrated = expected["integrated"] if isinstance(expected, dict) else expected.integrated
    exp_momentary = expected["momentary"] if isinstance(expected, dict) else expected.momentary
    assert result.integrated == exp_integrated
    assert list(result.momentary) == list(exp_momentary)
