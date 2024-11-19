import array

cimport cython
from libc.stdlib cimport free, malloc
from libc.string cimport memcpy, memset


DEF BUFFER_SIZE = 65536
DEF ALIGNMENT = 64


@cython.boundscheck(False)
@cython.wraparound(False)
# @cython.cdivision(True)
def convert_24bit_to_32bit(const unsigned char[:] data):
    cdef int len_data = data.size
    cdef int len_result = len_data // 3 * 4
    cdef int i, p = 0
    cdef int chunk_start, chunk_end
    cdef int chunk_size = BUFFER_SIZE
    cdef unsigned char b0, b1, b2
    cdef unsigned char* result_bytes = <unsigned char*> malloc(len_result * sizeof(unsigned char))
    cdef unsigned int temp_val
    cdef:
        unsigned char* source = <unsigned char*>&data[0]
        unsigned char* dest
        int src_step = 3
        int dest_step = 4
        int samples = len_data // 3
        int offset = 0

    if result_bytes == NULL:
        raise MemoryError("Could not allocate memory for result array")

    try:
        # dest = result_bytes

        for i in range(samples):
            # dest[0] = (source[2] >> 7) * 0xff
            # memcpy(dest + 1, source, 3)
            result_bytes[i * 4] = (source[2] >> 7) * 0xff
            memcpy(result_bytes + (i * 4) + 1, source, 3)
            source += src_step
            # dest += dest_step

        return bytes(result_bytes[:len_result])
    finally:
        free(result_bytes)
