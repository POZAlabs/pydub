use pyo3::prelude::*;

mod overlay;

#[pymodule]
fn _pydub_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(overlay::overlay_segments, m)?)?;
    Ok(())
}
