# Pydub (Pozalabs Fork)

Pydub lets you do stuff to audio in a way that isn't stupid.

This is a [Pozalabs](https://github.com/Pozalabs) fork of [jiaaro/pydub](https://github.com/jiaaro/pydub), published as `pozalabs-pydub` on PyPI.

## Changes from Upstream

### Requirements

- Python 3.11+ (upstream supports Python 2.7+)
- All legacy Python 2 compatibility code has been removed

### Performance (Cython Extensions)

- `overlay.pyx` - Cython-optimized audio overlay with bounds checking disabled and C-level division
- `sample.pyx` - Cython-optimized 24-bit to 32-bit sample extension using direct memory operations
- `fade()` - Memory-efficient fade using `memoryview`, with coarse/precise two-path implementation
- 24-bit `AudioSegment` initialization allocates significantly less memory

### New Features

- **Compressed audio I/O** - `from_file()` auto-detects and decompresses gzip/zstd files; `export()` accepts an optional `compressor` parameter
- **Audio level metering** - `measure_audio_level()` for RMS, peak, and LUFS measurement (requires optional `audiometer` dependency)
- **Waveform data** - `get_normalized_amplitudes()` computes normalized amplitude values for waveform visualization
- **Silent audio generation** - Create silent audio matching the original segment's parameters
- **Audio processing framework** - Command-based processor architecture for merge, overlay, and format conversion
- **Python 3.13 support** - Via `audioop-lts` dependency

### Type Safety

- Comprehensive type hints using `Self`, `Literal`, `TypedDict`, `Unpack`
- `_AudioParams` dataclass with validation for initialization parameters

### Build System

- Migrated from `setup.py` to `pyproject.toml` with Poetry
- Custom `build.py` for Cython compilation with `-march=native -O3` flags

### Optional Dependencies

- `audiometer` (>=0.17.0) - Audio level metering (`pip install pozalabs-pydub[meter]`)
- `zstandard` (>=0.23.0) - Zstandard compression (`pip install pozalabs-pydub[zstd]`)

For general usage, API documentation, and ffmpeg setup, see the [upstream README](https://github.com/jiaaro/pydub#readme).

## License

[MIT License](http://opensource.org/licenses/mit-license.php) - Copyright 2011 James Robert
