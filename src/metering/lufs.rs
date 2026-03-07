use crate::types;
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

#[pyfunction]
pub fn measure_loudness(
    py: Python<'_>,
    samples: types::Samples,
    channels: u32,
    max_amplitude: f64,
    sample_rate: u32,
) -> PyResult<Loudness> {
    let (integrated, momentary_values) = py.detach(|| {
        let mut meter =
            ebur128::EbuR128::new(channels, sample_rate, ebur128::Mode::I | ebur128::Mode::M)
                .map_err(|e| PyValueError::new_err(e.to_string()))?;

        let samples_in_100ms = (sample_rate as usize + 5) / 10;
        let chunk_size = channels as usize * samples_in_100ms;
        let mut momentary = Vec::new();
        for chunk in samples.normalized_source(max_amplitude).chunks(chunk_size) {
            meter
                .add_frames_f64(chunk)
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            if let Ok(m) = meter.loudness_momentary() {
                momentary.push(m);
            }
        }
        let integrated = meter.loudness_global().unwrap_or(f64::NEG_INFINITY);

        Ok::<_, PyErr>((integrated, momentary))
    })?;

    let momentary = PyList::new(py, &momentary_values)?.into();

    Ok(Loudness {
        integrated,
        momentary,
    })
}
