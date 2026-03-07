use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

#[pyfunction]
pub fn extend_24bit_to_32bit<'py>(py: Python<'py>, data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let input_size = data.len();
    if input_size % 3 != 0 {
        return Err(PyValueError::new_err(
            "Input size must be a multiple of 3 bytes",
        ));
    }

    let num_samples = input_size / 3;
    let output_size = num_samples * 4;

    let output = PyBytes::new_with(py, output_size, |out_buf| {
        unsafe {
            let input_ptr = data.as_ptr();
            let output_ptr = out_buf.as_mut_ptr();

            for i in 0..num_samples {
                let src = input_ptr.add(i * 3);
                let dst = output_ptr.add(i * 4);

                *dst = if *src.add(2) & 0x80 != 0 { 0xFF } else { 0x00 };
                std::ptr::copy_nonoverlapping(src, dst.add(1), 3);
            }
        }

        Ok(())
    })?;

    Ok(output)
}

#[cfg(test)]
mod tests {

    #[test]
    fn test_positive_sample() {
        // 24-bit positive sample: 0x01 0x02 0x03 (MSB=0x03, no sign bit)
        let input = [0x01, 0x02, 0x03];
        let output = extend_24bit_inner(&input);
        assert_eq!(output, [0x00, 0x01, 0x02, 0x03]);
    }

    #[test]
    fn test_negative_sample() {
        // 24-bit negative sample: 0x01 0x02 0x83 (MSB=0x83, sign bit set)
        let input = [0x01, 0x02, 0x83];
        let output = extend_24bit_inner(&input);
        assert_eq!(output, [0xFF, 0x01, 0x02, 0x83]);
    }

    #[test]
    fn test_zero_sample() {
        let input = [0x00, 0x00, 0x00];
        let output = extend_24bit_inner(&input);
        assert_eq!(output, [0x00, 0x00, 0x00, 0x00]);
    }

    #[test]
    fn test_multiple_samples() {
        // Two samples: positive then negative
        let input = [0x01, 0x02, 0x03, 0x04, 0x05, 0x86];
        let output = extend_24bit_inner(&input);
        assert_eq!(output, [0x00, 0x01, 0x02, 0x03, 0xFF, 0x04, 0x05, 0x86]);
    }

    fn extend_24bit_inner(data: &[u8]) -> Vec<u8> {
        let num_samples = data.len() / 3;
        let mut output = vec![0u8; num_samples * 4];
        unsafe {
            let input_ptr = data.as_ptr();
            let output_ptr = output.as_mut_ptr();
            for i in 0..num_samples {
                let src = input_ptr.add(i * 3);
                let dst = output_ptr.add(i * 4);
                *dst = if *src.add(2) & 0x80 != 0 { 0xFF } else { 0x00 };
                std::ptr::copy_nonoverlapping(src, dst.add(1), 3);
            }
        }
        output
    }
}
