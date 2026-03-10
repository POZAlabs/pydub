# Pydub (Pozalabs Fork)

Pydub lets you do stuff to audio in a way that isn't stupid.

This is a [Pozalabs](https://github.com/Pozalabs) fork of [jiaaro/pydub](https://github.com/jiaaro/pydub), published as `pozalabs-pydub` on PyPI.

## Changes from Upstream

### Requirements

- Python 3.11+ (upstream supports Python 2.7+)
- All legacy Python 2 compatibility code has been removed

### Performance (Rust/PyO3 Extensions)

- `overlay_segments` - Pre-allocated buffer overlay replacing audioop.add/mul (16-bit 4-5x, 32-bit 11-16x faster)
- `extend_24bit_to_32bit` - Zero-copy 24-bit to 32-bit sample extension via direct PyBytes allocation (~400x faster than pure Python)
- `fade_segment` - Rust 단일 패스 fade 처리로 audioop.mul 루프 대체 (fade/fade_in/fade_out)

### New Features

- **Compressed audio I/O** - `from_file()` auto-detects and decompresses gzip/zstd files; `export()` accepts an optional `compressor` parameter
- **Audio level metering** - `measure_audio_level()` for RMS, peak, and LUFS measurement
- **Waveform data** - `get_normalized_amplitudes()` computes normalized amplitude values for waveform visualization
- **Silent audio generation** - Create silent audio matching the original segment's parameters
- **Audio processing framework** - Command-based processor architecture for merge, overlay, and format conversion
- **Python 3.13 support** - Via `audioop-lts` dependency

### Type Safety

- Comprehensive type hints using `Self`, `Literal`, `TypedDict`, `Unpack`
- `_AudioParams` dataclass with validation for initialization parameters

### Build System

- `pyproject.toml` with maturin backend, managed by uv
- Rust(PyO3) native extension compiled via maturin
- Wheel distribution via GitHub Actions

### Dependencies

- `backports.zstd` (>=1.3.0) - Zstandard compression (Python <3.14, stdlib `compression.zstd` on 3.14+)

For general usage, API documentation, and ffmpeg setup, see the [upstream README](https://github.com/jiaaro/pydub#readme).

## License

[MIT License](http://opensource.org/licenses/mit-license.php) - Copyright 2011 James Robert
