use crate::types;
use crate::utils::ratio_to_db;
use pyo3::prelude::*;

const EMA_TIME_CONSTANT: f64 = 0.3 / 2.0;
const AES17_RMS_CORRECTION: f64 = 2.0;

#[pyfunction]
pub fn measure_rms(
    py: Python,
    samples: types::Samples,
    channels: u32,
    max_amplitude: f64,
    sample_rate: u32,
) -> f64 {
    py.detach(|| {
        let channels = channels as usize;
        let decay_const = (-1.0 / sample_rate as f64 / EMA_TIME_CONSTANT).exp();
        let update_ratio = 1.0 - decay_const;

        let mut max_rms: f64 = 0.0;
        for i in 0..channels {
            let mut channel_max_rms: f64 = 0.0;
            let mut current_rms: f64 = 0.0;
            for channel_sample in samples.source[i..].iter().step_by(channels) {
                let sample = (*channel_sample as f64 / max_amplitude).abs();
                current_rms = (current_rms * decay_const) + (sample * sample * update_ratio);
                channel_max_rms = channel_max_rms.max(current_rms);
            }

            max_rms = max_rms.max(channel_max_rms);
        }

        ratio_to_db(max_rms * AES17_RMS_CORRECTION, false)
    })
}
