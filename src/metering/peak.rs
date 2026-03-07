use crate::types;
use crate::utils::ratio_to_db;
use pyo3::prelude::*;

#[pyfunction]
pub fn measure_peak(py: Python, samples: types::Samples, channels: u32, max_amplitude: f64) -> f64 {
    py.detach(|| {
        let channels = channels as usize;
        let mut max_peak: f64 = 0.0;
        for i in 0..channels {
            let mut channel_max_peak: f64 = 0.0;
            for channel_sample in samples.source[i..].iter().step_by(channels) {
                let sample = (*channel_sample as f64 / max_amplitude).abs();
                channel_max_peak = channel_max_peak.max(sample)
            }

            max_peak = max_peak.max(channel_max_peak)
        }

        ratio_to_db(max_peak, true)
    })
}
