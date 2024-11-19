import array

cimport cython
from libc.stdlib cimport free, malloc


DEF BUFFER_SIZE = 65536


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def convert_24bit_to_32bit(const unsigned char[:] data):
    cdef int len_data = data.size
    cdef int len_result = len_data // 3 * 4
    cdef int i, p = 0
    cdef int chunk_start, chunk_end
    cdef int chunk_size = BUFFER_SIZE
    cdef unsigned char b0, b1, b2
    cdef unsigned char *result_bytes = <unsigned char *> malloc(len_result * sizeof(unsigned char))

    if result_bytes == NULL:
        raise MemoryError("Could not allocate memory for result array")

    try:
        for chunk_start in range(0, len_data, chunk_size):
            chunk_end = min(chunk_start + chunk_size, len_data - 2)

            for i in range(chunk_start, chunk_end, 3):
                b0 = data[i]
                b1 = data[i + 1]
                b2 = data[i + 2]

                result_bytes[p] = (b2 >> 7) * 0xff
                result_bytes[p + 1] = b0
                result_bytes[p + 2] = b1
                result_bytes[p + 3] = b2

                p += 4

        return bytes(result_bytes[:len_result])
    finally:
        free(result_bytes)
