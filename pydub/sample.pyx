cimport cython
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AS_STRING
from libc.string cimport memcpy, memset


DEF BYTES_PER_24BIT_SAMPLE = 3
DEF BYTES_PER_32BIT_SAMPLE = 4


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def extend_24bit_to_32bit(const unsigned char[::1] data):  # Use contiguous memory view
    cdef:
        int input_size = data.shape[0]  # More efficient than data.size
        int output_size
        int num_samples
        int sample_idx = 0
        const unsigned char* input_ptr
        unsigned char* output_buffer
        object output_bytes
        unsigned char sign_bit

    # Validate input size
    if input_size % BYTES_PER_24BIT_SAMPLE:
        raise ValueError("Input size must be a multiple of 3 bytes")

    # Pre-calculate sizes once
    num_samples = input_size // BYTES_PER_24BIT_SAMPLE
    output_size = num_samples * BYTES_PER_32BIT_SAMPLE

    # Get input pointer directly from contiguous memory view
    input_ptr = &data[0]

    # Create output bytes with exact size needed
    output_bytes = PyBytes_FromStringAndSize(NULL, output_size)
    if not output_bytes:
        raise MemoryError("Could not allocate memory for output")

    # Get direct pointer to output buffer
    output_buffer = <unsigned char*>PyBytes_AS_STRING(output_bytes)

    for sample_idx in range(num_samples):
        sign_bit = (input_ptr[sample_idx * BYTES_PER_24BIT_SAMPLE + 2] >> 7) * 0xff

        output_buffer[sample_idx * BYTES_PER_32BIT_SAMPLE] = sign_bit
        output_buffer[sample_idx * BYTES_PER_32BIT_SAMPLE + 1] = input_ptr[sample_idx * BYTES_PER_24BIT_SAMPLE]
        output_buffer[sample_idx * BYTES_PER_32BIT_SAMPLE + 2] = input_ptr[sample_idx * BYTES_PER_24BIT_SAMPLE + 1]
        output_buffer[sample_idx * BYTES_PER_32BIT_SAMPLE + 3] = input_ptr[sample_idx * BYTES_PER_24BIT_SAMPLE + 2]

    return output_bytes
