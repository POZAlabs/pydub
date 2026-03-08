use super::sample::{cast_samples, validate_data, Sample};
use crate::utils::ratio_to_db;
use pyo3::prelude::*;

const EMA_TIME_CONSTANT: f64 = 0.3 / 2.0;
const AES17_RMS_CORRECTION: f64 = 2.0;

fn compute_rms<T: Sample>(samples: &[T], channels: usize, sample_rate: u32) -> f64 {
    let max_amplitude = T::max_amplitude();
    let decay_const = (-1.0 / sample_rate as f64 / EMA_TIME_CONSTANT).exp();
    let update_ratio = 1.0 - decay_const;

    let mut max_rms: f64 = 0.0;
    for i in 0..channels {
        let mut channel_max_rms: f64 = 0.0;
        let mut current_rms: f64 = 0.0;
        for channel_sample in samples[i..].iter().step_by(channels) {
            let sample = (channel_sample.to_f64() / max_amplitude).abs();
            current_rms = (current_rms * decay_const) + (sample * sample * update_ratio);
            channel_max_rms = channel_max_rms.max(current_rms);
        }
        max_rms = max_rms.max(channel_max_rms);
    }

    ratio_to_db(max_rms * AES17_RMS_CORRECTION, false)
}

#[pyfunction]
pub fn measure_rms(
    py: Python,
    data: &[u8],
    sample_width: u8,
    channels: u32,
    sample_rate: u32,
) -> PyResult<f64> {
    validate_data(data, sample_width)?;
    let channels = channels as usize;
    let ptr = data.as_ptr() as usize;
    let len = data.len();
    Ok(py.detach(|| {
        let data = unsafe { std::slice::from_raw_parts(ptr as *const u8, len) };
        match sample_width {
            1 => compute_rms(unsafe { cast_samples::<i8>(data) }, channels, sample_rate),
            2 => compute_rms(unsafe { cast_samples::<i16>(data) }, channels, sample_rate),
            4 => compute_rms(unsafe { cast_samples::<i32>(data) }, channels, sample_rate),
            _ => unreachable!(),
        }
    }))
}
