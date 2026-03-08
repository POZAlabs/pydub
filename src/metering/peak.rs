use super::sample::{cast_samples, validate_data, Sample};
use crate::utils::ratio_to_db;
use pyo3::prelude::*;

fn compute_peak<T: Sample>(samples: &[T], channels: usize) -> f64 {
    let max_amplitude = T::max_amplitude();
    let mut max_peak: f64 = 0.0;
    for i in 0..channels {
        let mut channel_max_peak: f64 = 0.0;
        for channel_sample in samples[i..].iter().step_by(channels) {
            let sample = (channel_sample.to_f64() / max_amplitude).abs();
            channel_max_peak = channel_max_peak.max(sample);
        }
        max_peak = max_peak.max(channel_max_peak);
    }

    ratio_to_db(max_peak, true)
}

#[pyfunction]
pub fn measure_peak(
    py: Python,
    data: &[u8],
    sample_width: u8,
    channels: u32,
) -> PyResult<f64> {
    validate_data(data, sample_width)?;
    let channels = channels as usize;
    let ptr = data.as_ptr() as usize;
    let len = data.len();
    Ok(py.detach(|| {
        let data = unsafe { std::slice::from_raw_parts(ptr as *const u8, len) };
        match sample_width {
            1 => compute_peak(unsafe { cast_samples::<i8>(data) }, channels),
            2 => compute_peak(unsafe { cast_samples::<i16>(data) }, channels),
            4 => compute_peak(unsafe { cast_samples::<i32>(data) }, channels),
            _ => unreachable!(),
        }
    }))
}
