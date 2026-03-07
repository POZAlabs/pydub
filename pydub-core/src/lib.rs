use pyo3::prelude::*;

mod overlay;
mod sample;

#[pymodule]
fn _pydub_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(overlay::overlay_segments, m)?)?;
    m.add_function(wrap_pyfunction!(sample::extend_24bit_to_32bit, m)?)?;
    Ok(())
}
