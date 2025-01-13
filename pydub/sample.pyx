cimport cython
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AS_STRING
from libc.string cimport memcpy


DEF BYTES_PER_24BIT_SAMPLE = 3
DEF BYTES_PER_32BIT_SAMPLE = 4


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def extend_24bit_to_32bit(const unsigned char[::1] data):
    cdef:
        int input_size = data.shape[0]
        int output_size
        int num_samples
        int sample_idx = 0
        const unsigned char* input_ptr
        unsigned char* output_buffer
        object output_bytes
        unsigned char sign_bit

    if input_size % BYTES_PER_24BIT_SAMPLE:
        raise ValueError("Input size must be a multiple of 3 bytes")

    num_samples = input_size // BYTES_PER_24BIT_SAMPLE
    output_size = num_samples * BYTES_PER_32BIT_SAMPLE

    input_ptr = &data[0]

    output_bytes = PyBytes_FromStringAndSize(NULL, output_size)
    if not output_bytes:
        raise MemoryError("Could not allocate memory for output")

    output_buffer = <unsigned char*>PyBytes_AS_STRING(output_bytes)

    for sample_idx in range(num_samples):
        # Extend sign bit
        output_buffer[sample_idx * BYTES_PER_32BIT_SAMPLE] = (input_ptr[2] >> 7) * 0xff
        # Copy last 3 bytes from source
        memcpy(output_buffer + (sample_idx * BYTES_PER_32BIT_SAMPLE) + 1, input_ptr, BYTES_PER_24BIT_SAMPLE)
        input_ptr += BYTES_PER_24BIT_SAMPLE

    return output_bytes
