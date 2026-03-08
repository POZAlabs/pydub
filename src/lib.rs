use pyo3::prelude::*;

mod metering;
mod overlay;
mod sample;
pub(crate) mod utils;

#[pymodule]
fn _pydub_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(overlay::overlay_segments, m)?)?;
    m.add_function(wrap_pyfunction!(sample::extend_24bit_to_32bit, m)?)?;
    m.add_function(wrap_pyfunction!(metering::rms::measure_rms, m)?)?;
    m.add_function(wrap_pyfunction!(metering::peak::measure_peak, m)?)?;
    m.add_class::<metering::lufs::Loudness>()?;
    m.add_function(wrap_pyfunction!(metering::lufs::measure_loudness, m)?)?;
    Ok(())
}
