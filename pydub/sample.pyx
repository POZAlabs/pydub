import array

cimport cython
from libc.stdlib cimport free, malloc


@cython.boundscheck(False)
@cython.wraparound(False)
def convert_24bit_to_32bit(unsigned char[:] data):
    cdef int i
    cdef int p = 0
    cdef int len_data = data.size
    cdef int len_result = len_data // 3 * 4
    cdef unsigned char b0, b1, b2
    cdef unsigned char *result_bytes = <unsigned char *> malloc(len_result * sizeof(unsigned char))

    if result_bytes == NULL:
        raise MemoryError("Could not allocate memory for result array")

    try:
        for i in range(0, len_data, 3):
            b0 = data[i]
            b1 = data[i + 1]
            b2 = data[i + 2]

            result_bytes[p] = 0xFF if b2 > 0x7f else 0x00
            result_bytes[p + 1] = b0
            result_bytes[p + 2] = b1
            result_bytes[p + 3] = b2

            p += 4

        return array.array("B", result_bytes[:len_result])
    finally:
        free(result_bytes)
