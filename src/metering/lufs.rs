use super::sample::{cast_samples, validate_data, Sample};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyList;

#[pyclass(frozen)]
pub struct Loudness {
    #[pyo3(get)]
    pub integrated: f64,
    momentary: Py<PyList>,
}

#[pymethods]
impl Loudness {
    #[getter]
    fn momentary(&self, py: Python<'_>) -> Py<PyList> {
        self.momentary.clone_ref(py)
    }
}

fn compute_loudness<T: Sample>(
    samples: &[T],
    channels: u32,
    sample_rate: u32,
) -> Result<(f64, Vec<f64>), PyErr> {
    let max_amplitude = T::max_amplitude();
    let mut meter =
        ebur128::EbuR128::new(channels, sample_rate, ebur128::Mode::I | ebur128::Mode::M)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

    let samples_in_100ms = (sample_rate as usize + 5) / 10;
    let chunk_size = channels as usize * samples_in_100ms;
    let mut chunk_buf = vec![0.0f64; chunk_size];
    let mut momentary = Vec::new();
    for chunk in samples.chunks(chunk_size) {
        let buf = &mut chunk_buf[..chunk.len()];
        for (dst, src) in buf.iter_mut().zip(chunk.iter()) {
            *dst = src.to_f64() / max_amplitude;
        }
        meter
            .add_frames_f64(buf)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        if let Ok(m) = meter.loudness_momentary() {
            momentary.push(m);
        }
    }
    let integrated = meter.loudness_global().unwrap_or(f64::NEG_INFINITY);

    Ok((integrated, momentary))
}

#[pyfunction]
pub fn measure_loudness(
    py: Python<'_>,
    data: &[u8],
    sample_width: u8,
    channels: u32,
    sample_rate: u32,
) -> PyResult<Loudness> {
    validate_data(data, sample_width)?;
    let ptr = data.as_ptr() as usize;
    let len = data.len();
    let (integrated, momentary_values) = py.detach(|| {
        let data = unsafe { std::slice::from_raw_parts(ptr as *const u8, len) };
        match sample_width {
            1 => compute_loudness(unsafe { cast_samples::<i8>(data) }, channels, sample_rate),
            2 => compute_loudness(unsafe { cast_samples::<i16>(data) }, channels, sample_rate),
            4 => compute_loudness(unsafe { cast_samples::<i32>(data) }, channels, sample_rate),
            _ => unreachable!(),
        }
    })?;

    let momentary = PyList::new(py, &momentary_values)?.into();

    Ok(Loudness {
        integrated,
        momentary,
    })
}
