cimport cython
from libc.stdlib cimport free, malloc
from libc.string cimport memcpy, memset


DEF BYTES_PER_SAMPLE_24BIT = 3
DEF BYTES_PER_SAMPLE_32BIT = 4


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def extend_24bit_to_32bit(const unsigned char[:] data):
    cdef:
        int input_size = data.size
        int output_size = input_size // BYTES_PER_SAMPLE_24BIT * BYTES_PER_SAMPLE_32BIT
        int num_samples = input_size // BYTES_PER_SAMPLE_24BIT
        int sample_idx = 0
        unsigned char* input_ptr = <unsigned char*>&data[0]
        unsigned char* output_ptr = <unsigned char*> malloc(output_size * sizeof(unsigned char))

    if output_ptr == NULL:
        raise MemoryError("Could not allocate memory for result array")

    try:
        for sample_idx in range(num_samples):
            # Extend sign bit
            output_ptr[sample_idx * BYTES_PER_SAMPLE_32BIT] = (input_ptr[2] >> 7) * 0xff
            # Copy last 3 bytes from source
            memcpy(output_ptr + (sample_idx * BYTES_PER_SAMPLE_32BIT) + 1, input_ptr, BYTES_PER_SAMPLE_24BIT)
            input_ptr += BYTES_PER_SAMPLE_24BIT

        return bytes(output_ptr[:output_size])
    finally:
        free(output_ptr)
