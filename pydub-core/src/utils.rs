pub fn ratio_to_db(ratio: f64, using_amplitude: bool) -> f64 {
    if ratio == 0.0 {
        return f64::NEG_INFINITY;
    }

    let logarithm = ratio.log10();
    let multiplier = if using_amplitude { 20.0 } else { 10.0 };

    multiplier * logarithm
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ratio_zero() {
        assert!(ratio_to_db(0.0, true).is_infinite());
        assert!(ratio_to_db(0.0, true).is_sign_negative());
    }

    #[test]
    fn test_ratio_amplitude() {
        let result = ratio_to_db(2.0, true);
        assert!((result - 6.0206).abs() < 0.001);
    }

    #[test]
    fn test_ratio_power() {
        let result = ratio_to_db(2.0, false);
        assert!((result - 3.0103).abs() < 0.001);
    }
}
