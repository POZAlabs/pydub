cimport cython
from libc.stdlib cimport free, malloc
from cython.parallel import prange

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def convert_24bit_to_32bit(const unsigned char[:] data):
    cdef:
        int chunk_size = 1024 * 1024 * 10  # 1MB chunks
        int len_data = data.size
        int len_result = len_data // 3 * 4
        unsigned char *result_bytes = <unsigned char *> malloc(len_result * sizeof(unsigned char))
        int num_chunks = (len_data + chunk_size - 1) // chunk_size

    if result_bytes == NULL:
        raise MemoryError("Could not allocate memory for result array")

    try:
        with nogil:
            _process_chunks_parallel(data, result_bytes, len_data, chunk_size, num_chunks)
        return bytes(result_bytes[:len_result])
    finally:
        free(result_bytes)

cdef int _process_chunks_parallel(const unsigned char[:] data, unsigned char *result_bytes,
                                 int len_data, int chunk_size, int num_chunks) nogil:
    cdef:
        int chunk_idx, chunk_start, chunk_end
        int i, p
        unsigned char b0, b1, b2

    for chunk_idx in prange(num_chunks, schedule='guided'):
        chunk_start = chunk_idx * chunk_size
        chunk_end = min(chunk_start + chunk_size, len_data - 2)
        p = (chunk_start // 3) * 4

        # Process each 3-byte sample in the chunk
        for i in range(chunk_start, chunk_end, 3):
            # Load 3 bytes at once and process them
            b0 = data[i]
            b1 = data[i + 1]
            b2 = data[i + 2]

            # Use bitwise operations instead of conditionals
            result_bytes[p] = (b2 >> 7) * 0xff  # Sign extension
            result_bytes[p + 1] = b0
            result_bytes[p + 2] = b1
            result_bytes[p + 3] = b2

            p = p + 4

cdef inline unsigned char sign_extend(unsigned char msb) nogil:
    return (msb >> 7) * 0xff
