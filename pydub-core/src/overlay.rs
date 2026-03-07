use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

fn gain_8(sample: i8, factor: f64) -> i8 {
    let val = (sample as f64 * factor) as i16;
    val.clamp(i8::MIN as i16, i8::MAX as i16) as i8
}

fn mix_8(a: i8, b: i8) -> i8 {
    let val = a as i16 + b as i16;
    val.clamp(i8::MIN as i16, i8::MAX as i16) as i8
}

fn gain_16(sample: i16, factor: f64) -> i16 {
    let val = (sample as f64 * factor) as i32;
    val.clamp(i16::MIN as i32, i16::MAX as i32) as i16
}

fn mix_16(a: i16, b: i16) -> i16 {
    let val = a as i32 + b as i32;
    val.clamp(i16::MIN as i32, i16::MAX as i32) as i16
}

fn gain_32(sample: i32, factor: f64) -> i32 {
    let val = (sample as f64 * factor) as i64;
    val.clamp(i32::MIN as i64, i32::MAX as i64) as i32
}

fn mix_32(a: i32, b: i32) -> i32 {
    let val = a as i64 + b as i64;
    val.clamp(i32::MIN as i64, i32::MAX as i64) as i32
}

#[pyfunction]
#[pyo3(signature = (seg1_data, seg2_data, sample_width, position, times, gain_during_overlay=0))]
pub fn overlay_segments<'py>(
    py: Python<'py>,
    seg1_data: &[u8],
    seg2_data: &[u8],
    sample_width: i32,
    position: i32,
    times: i32,
    gain_during_overlay: i32,
) -> PyResult<Bound<'py, PyBytes>> {
    let seg1_len = seg1_data.len() as i32;
    let seg2_len = seg2_data.len() as i32;

    if position >= seg1_len {
        return Ok(PyBytes::new(py, seg1_data));
    }

    if !matches!(sample_width, 1 | 2 | 4) {
        return Err(PyValueError::new_err(format!(
            "sample_width must be 1, 2, or 4 (got {sample_width})"
        )));
    }

    if seg1_len % sample_width != 0 {
        return Err(PyValueError::new_err(
            "seg1_data length is not a multiple of sample_width",
        ));
    }

    if seg2_len % sample_width != 0 {
        return Err(PyValueError::new_err(
            "seg2_data length is not a multiple of sample_width",
        ));
    }

    if sample_width > 1 && position % sample_width != 0 {
        return Err(PyValueError::new_err(format!(
            "position ({position}) must be aligned to sample_width ({sample_width})"
        )));
    }

    let apply_gain = gain_during_overlay != 0;
    let db_factor = if apply_gain {
        10.0_f64.powf(gain_during_overlay as f64 / 20.0)
    } else {
        1.0
    };

    let seg1_len_u = seg1_len as usize;
    let output = PyBytes::new_with(py, seg1_len_u, |out_buf| {
        out_buf.copy_from_slice(seg1_data);

        let repeat_to_fill = times < 0;
        let mut remaining_times = times;
        let seg1_len_after_pos = seg1_len - position;
        let mut current_position: i32 = 0;
        let position = position as usize;
        let seg2_len = seg2_len as usize;

        match sample_width {
            1 => {
                while (repeat_to_fill || remaining_times > 0)
                    && current_position < seg1_len_after_pos
                {
                    let remaining = (seg1_len_after_pos - current_position) as usize;
                    let chunk_len = remaining.min(seg2_len);
                    let num_samples = chunk_len;
                    let offset = position + current_position as usize;

                    unsafe {
                        let out_ptr = out_buf.as_mut_ptr().add(offset) as *mut i8;
                        let s2_ptr = seg2_data.as_ptr() as *const i8;

                        for i in 0..num_samples {
                            let out_val = *out_ptr.add(i);
                            let s2_val = *s2_ptr.add(i);
                            if apply_gain {
                                *out_ptr.add(i) = mix_8(gain_8(out_val, db_factor), s2_val);
                            } else {
                                *out_ptr.add(i) = mix_8(out_val, s2_val);
                            }
                        }
                    }

                    current_position += chunk_len as i32;
                    if !repeat_to_fill {
                        remaining_times -= 1;
                    }
                }
            }
            2 => {
                while (repeat_to_fill || remaining_times > 0)
                    && current_position < seg1_len_after_pos
                {
                    let remaining = (seg1_len_after_pos - current_position) as usize;
                    let chunk_len = remaining.min(seg2_len);
                    let num_samples = chunk_len / 2;
                    let offset = position + current_position as usize;

                    unsafe {
                        let out_ptr = out_buf.as_mut_ptr().add(offset) as *mut i16;
                        let s2_ptr = seg2_data.as_ptr() as *const i16;

                        for i in 0..num_samples {
                            let out_val = *out_ptr.add(i);
                            let s2_val = *s2_ptr.add(i);
                            if apply_gain {
                                *out_ptr.add(i) = mix_16(gain_16(out_val, db_factor), s2_val);
                            } else {
                                *out_ptr.add(i) = mix_16(out_val, s2_val);
                            }
                        }
                    }

                    current_position += chunk_len as i32;
                    if !repeat_to_fill {
                        remaining_times -= 1;
                    }
                }
            }
            4 => {
                while (repeat_to_fill || remaining_times > 0)
                    && current_position < seg1_len_after_pos
                {
                    let remaining = (seg1_len_after_pos - current_position) as usize;
                    let chunk_len = remaining.min(seg2_len);
                    let num_samples = chunk_len / 4;
                    let offset = position + current_position as usize;

                    unsafe {
                        let out_ptr = out_buf.as_mut_ptr().add(offset) as *mut i32;
                        let s2_ptr = seg2_data.as_ptr() as *const i32;

                        for i in 0..num_samples {
                            let out_val = *out_ptr.add(i);
                            let s2_val = *s2_ptr.add(i);
                            if apply_gain {
                                *out_ptr.add(i) = mix_32(gain_32(out_val, db_factor), s2_val);
                            } else {
                                *out_ptr.add(i) = mix_32(out_val, s2_val);
                            }
                        }
                    }

                    current_position += chunk_len as i32;
                    if !repeat_to_fill {
                        remaining_times -= 1;
                    }
                }
            }
            _ => unreachable!(),
        }

        Ok(())
    })?;

    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gain_8_normal() {
        assert_eq!(gain_8(50, 2.0), 100);
        assert_eq!(gain_8(-50, 2.0), -100);
    }

    #[test]
    fn test_gain_8_clamp_overflow() {
        assert_eq!(gain_8(100, 2.0), 127);
    }

    #[test]
    fn test_gain_8_clamp_underflow() {
        assert_eq!(gain_8(-100, 2.0), -128);
    }

    #[test]
    fn test_mix_8_normal() {
        assert_eq!(mix_8(50, 30), 80);
        assert_eq!(mix_8(-50, -30), -80);
    }

    #[test]
    fn test_mix_8_clamp_overflow() {
        assert_eq!(mix_8(100, 100), 127);
    }

    #[test]
    fn test_mix_8_clamp_underflow() {
        assert_eq!(mix_8(-100, -100), -128);
    }

    #[test]
    fn test_gain_16_normal() {
        assert_eq!(gain_16(1000, 2.0), 2000);
        assert_eq!(gain_16(-1000, 2.0), -2000);
    }

    #[test]
    fn test_gain_16_clamp_overflow() {
        assert_eq!(gain_16(30000, 2.0), i16::MAX);
    }

    #[test]
    fn test_gain_16_clamp_underflow() {
        assert_eq!(gain_16(-30000, 2.0), i16::MIN);
    }

    #[test]
    fn test_mix_16_normal() {
        assert_eq!(mix_16(1000, 2000), 3000);
        assert_eq!(mix_16(-1000, -2000), -3000);
    }

    #[test]
    fn test_mix_16_clamp_overflow() {
        assert_eq!(mix_16(i16::MAX, 1), i16::MAX);
    }

    #[test]
    fn test_mix_16_clamp_underflow() {
        assert_eq!(mix_16(i16::MIN, -1), i16::MIN);
    }

    #[test]
    fn test_gain_32_normal() {
        assert_eq!(gain_32(100000, 2.0), 200000);
        assert_eq!(gain_32(-100000, 2.0), -200000);
    }

    #[test]
    fn test_gain_32_clamp_overflow() {
        assert_eq!(gain_32(2000000000, 2.0), i32::MAX);
    }

    #[test]
    fn test_gain_32_clamp_underflow() {
        assert_eq!(gain_32(-2000000000, 2.0), i32::MIN);
    }

    #[test]
    fn test_mix_32_normal() {
        assert_eq!(mix_32(100000, 200000), 300000);
        assert_eq!(mix_32(-100000, -200000), -300000);
    }

    #[test]
    fn test_mix_32_clamp_overflow() {
        assert_eq!(mix_32(i32::MAX, 1), i32::MAX);
    }

    #[test]
    fn test_mix_32_clamp_underflow() {
        assert_eq!(mix_32(i32::MIN, -1), i32::MIN);
    }
}
