use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

macro_rules! fade_impl {
    ($sample_type:ty, $wider_type:ty, $data:expr, $start:expr, $end:expr, $from_power:expr, $to_power:expr, $out:expr) => {{
        let sample_size = std::mem::size_of::<$sample_type>();

        if $from_power != 1.0 && $start > 0 {
            let before_samples = $start / sample_size;
            let src = unsafe {
                std::slice::from_raw_parts($data.as_ptr() as *const $sample_type, before_samples)
            };
            let dst = unsafe {
                std::slice::from_raw_parts_mut(
                    $out.as_mut_ptr() as *mut $sample_type,
                    before_samples,
                )
            };
            for i in 0..before_samples {
                let val = (src[i] as f64 * $from_power) as $wider_type;
                dst[i] = val.clamp(
                    <$sample_type>::MIN as $wider_type,
                    <$sample_type>::MAX as $wider_type,
                ) as $sample_type;
            }
        } else {
            $out[..$start].copy_from_slice(&$data[..$start]);
        }

        let fade_start_sample = $start / sample_size;
        let fade_end_sample = $end / sample_size;
        let fade_samples = fade_end_sample - fade_start_sample;
        if fade_samples > 0 {
            let gain_delta = $to_power - $from_power;
            let scale_step = gain_delta / fade_samples as f64;
            let src = unsafe {
                std::slice::from_raw_parts(
                    $data.as_ptr().add($start) as *const $sample_type,
                    fade_samples,
                )
            };
            let dst = unsafe {
                std::slice::from_raw_parts_mut(
                    $out.as_mut_ptr().add($start) as *mut $sample_type,
                    fade_samples,
                )
            };
            for i in 0..fade_samples {
                let gain = $from_power + scale_step * i as f64;
                let val = (src[i] as f64 * gain) as $wider_type;
                dst[i] = val.clamp(
                    <$sample_type>::MIN as $wider_type,
                    <$sample_type>::MAX as $wider_type,
                ) as $sample_type;
            }
        }

        if $to_power != 1.0 && $end < $data.len() {
            let after_samples = ($data.len() - $end) / sample_size;
            let src = unsafe {
                std::slice::from_raw_parts(
                    $data.as_ptr().add($end) as *const $sample_type,
                    after_samples,
                )
            };
            let dst = unsafe {
                std::slice::from_raw_parts_mut(
                    $out.as_mut_ptr().add($end) as *mut $sample_type,
                    after_samples,
                )
            };
            for i in 0..after_samples {
                let val = (src[i] as f64 * $to_power) as $wider_type;
                dst[i] = val.clamp(
                    <$sample_type>::MIN as $wider_type,
                    <$sample_type>::MAX as $wider_type,
                ) as $sample_type;
            }
        } else {
            $out[$end..].copy_from_slice(&$data[$end..]);
        }
    }};
}

fn fade_raw(
    data: &[u8],
    sample_width: u8,
    start_byte: usize,
    end_byte: usize,
    from_power: f64,
    to_power: f64,
    out: &mut [u8],
) {
    match sample_width {
        1 => fade_impl!(i8, i16, data, start_byte, end_byte, from_power, to_power, out),
        2 => fade_impl!(i16, i32, data, start_byte, end_byte, from_power, to_power, out),
        4 => fade_impl!(i32, i64, data, start_byte, end_byte, from_power, to_power, out),
        _ => unreachable!(),
    }
}

#[pyfunction]
pub fn fade_segment<'py>(
    py: Python<'py>,
    data: &[u8],
    sample_width: u8,
    start_byte: usize,
    end_byte: usize,
    from_power: f64,
    to_power: f64,
) -> PyResult<Bound<'py, PyBytes>> {
    if !matches!(sample_width, 1 | 2 | 4) {
        return Err(PyValueError::new_err(format!(
            "sample_width must be 1, 2, or 4 (got {sample_width})"
        )));
    }

    let sw = sample_width as usize;
    if data.len() % sw != 0 || start_byte % sw != 0 || end_byte % sw != 0 {
        return Err(PyValueError::new_err("byte offsets must be aligned to sample_width"));
    }

    if start_byte > end_byte || end_byte > data.len() {
        return Err(PyValueError::new_err("invalid start_byte/end_byte range"));
    }

    let output = PyBytes::new_with(py, data.len(), |out_buf| {
        fade_raw(data, sample_width, start_byte, end_byte, from_power, to_power, out_buf);
        Ok(())
    })?;

    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn apply_fade(data: &[u8], sw: u8, start: usize, end: usize, from: f64, to: f64) -> Vec<u8> {
        let mut out = vec![0u8; data.len()];
        fade_raw(data, sw, start, end, from, to, &mut out);
        out
    }

    fn to_i16_samples(data: &[u8]) -> Vec<i16> {
        data.chunks_exact(2)
            .map(|c| i16::from_ne_bytes([c[0], c[1]]))
            .collect()
    }

    fn to_i32_samples(data: &[u8]) -> Vec<i32> {
        data.chunks_exact(4)
            .map(|c| i32::from_ne_bytes([c[0], c[1], c[2], c[3]]))
            .collect()
    }

    // --- 8-bit ---

    #[test]
    fn test_8bit_linear() {
        let data: Vec<u8> = vec![100i8, 100, 100, 100].iter().map(|s| *s as u8).collect();
        let out = apply_fade(&data, 1, 0, data.len(), 0.0, 1.0);
        let samples: Vec<i8> = out.iter().map(|b| *b as i8).collect();
        assert_eq!(samples, [0, 25, 50, 75]);
    }

    #[test]
    fn test_8bit_no_change() {
        let data: Vec<u8> = vec![10i8, 20, 30, 40].iter().map(|s| *s as u8).collect();
        let out = apply_fade(&data, 1, 0, data.len(), 1.0, 1.0);
        assert_eq!(out, data);
    }

    #[test]
    fn test_8bit_clamp() {
        let data: Vec<u8> = vec![i8::MAX as u8, i8::MIN as u8];
        let out = apply_fade(&data, 1, 0, data.len(), 2.0, 2.0);
        assert_eq!(out[0] as i8, i8::MAX);
        assert_eq!(out[1] as i8, i8::MIN);
    }

    // --- 16-bit ---

    #[test]
    fn test_16bit_linear() {
        let data: Vec<u8> = vec![1000i16, 1000, 1000, 1000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        let out = apply_fade(&data, 2, 0, data.len(), 0.0, 1.0);
        assert_eq!(to_i16_samples(&out), [0, 250, 500, 750]);
    }

    #[test]
    fn test_16bit_no_change() {
        let data: Vec<u8> = vec![1000i16, 2000, 3000, 4000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        let out = apply_fade(&data, 2, 0, data.len(), 1.0, 1.0);
        assert_eq!(out, data);
    }

    #[test]
    fn test_16bit_clamp() {
        let data: Vec<u8> = vec![i16::MAX, i16::MAX]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        let out = apply_fade(&data, 2, 0, data.len(), 2.0, 2.0);
        assert_eq!(to_i16_samples(&out), [i16::MAX, i16::MAX]);
    }

    // --- 32-bit ---

    #[test]
    fn test_32bit_linear() {
        let data: Vec<u8> = vec![100_000i32, 100_000, 100_000, 100_000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        let out = apply_fade(&data, 4, 0, data.len(), 0.0, 1.0);
        assert_eq!(to_i32_samples(&out), [0, 25_000, 50_000, 75_000]);
    }

    #[test]
    fn test_32bit_no_change() {
        let data: Vec<u8> = vec![100_000i32, 200_000, 300_000, 400_000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        let out = apply_fade(&data, 4, 0, data.len(), 1.0, 1.0);
        assert_eq!(out, data);
    }

    #[test]
    fn test_32bit_clamp() {
        let data: Vec<u8> = vec![i32::MAX, i32::MIN]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        let out = apply_fade(&data, 4, 0, data.len(), 2.0, 2.0);
        assert_eq!(to_i32_samples(&out), [i32::MAX, i32::MIN]);
    }

    // --- edge cases ---

    #[test]
    fn test_empty_fade_region() {
        let data: Vec<u8> = vec![1000i16, 2000, 3000, 4000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        // start_byte == end_byte: no fade region, before gets from_power, after gets to_power
        let out = apply_fade(&data, 2, 4, 4, 0.5, 2.0);
        let samples = to_i16_samples(&out);
        assert_eq!(samples, [500, 1000, 6000, 8000]);
    }

    #[test]
    fn test_full_range_fade() {
        let data: Vec<u8> = vec![1000i16, 1000, 1000, 1000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        // entire data is fade region, no before/after
        let out = apply_fade(&data, 2, 0, data.len(), 0.0, 1.0);
        assert_eq!(to_i16_samples(&out), [0, 250, 500, 750]);
    }

    #[test]
    fn test_fade_at_start() {
        let data: Vec<u8> = vec![1000i16, 1000, 1000, 1000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        // fade first 2 samples, after region copies as-is (to_power=1.0)
        let out = apply_fade(&data, 2, 0, 4, 0.0, 1.0);
        let samples = to_i16_samples(&out);
        assert_eq!(samples[0], 0);
        assert_eq!(samples[1], 500);
        assert_eq!(samples[2], 1000);
        assert_eq!(samples[3], 1000);
    }

    #[test]
    fn test_fade_at_end() {
        let data: Vec<u8> = vec![1000i16, 1000, 1000, 1000]
            .iter()
            .flat_map(|s| s.to_ne_bytes())
            .collect();
        // before region copies as-is (from_power=1.0), fade last 2 samples
        let out = apply_fade(&data, 2, 4, 8, 1.0, 0.0);
        let samples = to_i16_samples(&out);
        assert_eq!(samples[0], 1000);
        assert_eq!(samples[1], 1000);
        assert_eq!(samples[2], 1000);
        assert_eq!(samples[3], 500);
    }
}
