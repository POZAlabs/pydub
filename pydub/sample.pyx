cimport cython
from libc.stdlib cimport free, malloc
from libc.string cimport memcpy, memset


DEF BYTES_PER_24BIT_SAMPLE = 3
DEF BYTES_PER_32BIT_SAMPLE = 4


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def extend_24bit_to_32bit(const unsigned char[:] data):
    cdef:
        int input_size = data.size
        int output_size = input_size // BYTES_PER_24BIT_SAMPLE * BYTES_PER_32BIT_SAMPLE
        int num_samples = input_size // BYTES_PER_24BIT_SAMPLE
        int sample_idx = 0
        unsigned char* input_ptr = <unsigned char*>&data[0]
        unsigned char* output_ptr = <unsigned char*> malloc(output_size * sizeof(unsigned char))

    if output_ptr == NULL:
        raise MemoryError("Could not allocate memory for result array")

    try:
        for sample_idx in range(num_samples):
            # Extend sign bit
            output_ptr[sample_idx * BYTES_PER_32BIT_SAMPLE] = (input_ptr[2] >> 7) * 0xff
            # Copy last 3 bytes from source
            memcpy(output_ptr + (sample_idx * BYTES_PER_32BIT_SAMPLE) + 1, input_ptr, BYTES_PER_24BIT_SAMPLE)
            input_ptr += BYTES_PER_24BIT_SAMPLE

        return bytes(output_ptr[:output_size])
    finally:
        free(output_ptr)
