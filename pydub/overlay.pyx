cimport cython
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AS_STRING
from libc.limits cimport SHRT_MAX, SHRT_MIN, INT_MAX, INT_MIN
from libc.string cimport memcpy
import audioop


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def overlay_segments(
    bytes seg1_data,
    bytes seg2_data,
    int sample_width,
    int position,
    int times,
    int gain_during_overlay = 0,
):
    cdef int seg1_len = len(seg1_data)
    cdef int seg2_len = len(seg2_data)
    cdef int remaining_times = times
    cdef int current_position
    cdef int remaining, chunk_len, num_samples, i
    cdef double db_factor = 1.0
    cdef int apply_gain = gain_during_overlay != 0

    cdef char* out_buf
    cdef const char* seg1_ptr
    cdef const char* seg2_ptr
    cdef object output_bytes

    cdef short* out_16
    cdef const short* s2_16
    cdef int val_32

    cdef int* out_32
    cdef const int* s2_32
    cdef long long val_64

    if position >= seg1_len:
        return seg1_data

    if sample_width in (2, 4) and position % sample_width != 0:
        raise ValueError(f"position ({position}) must be aligned to sample_width ({sample_width})")

    if apply_gain:
        db_factor = 10 ** (gain_during_overlay / 20.0)

    output_bytes = PyBytes_FromStringAndSize(NULL, seg1_len)
    out_buf = PyBytes_AS_STRING(output_bytes)
    seg1_ptr = <const char*>seg1_data
    seg2_ptr = <const char*>seg2_data
    memcpy(out_buf, seg1_ptr, seg1_len)

    cdef int seg1_len_after_pos = seg1_len - position
    current_position = 0

    if sample_width == 2:
        while True:
            if remaining_times == 0:
                break
            if current_position >= seg1_len_after_pos:
                break

            remaining = seg1_len_after_pos - current_position
            chunk_len = remaining if remaining < seg2_len else seg2_len
            num_samples = chunk_len // 2

            out_16 = <short*>(out_buf + position + current_position)
            s2_16 = <const short*>seg2_ptr

            if apply_gain:
                for i in range(num_samples):
                    val_32 = <int>(<double>out_16[i] * db_factor)
                    if val_32 > SHRT_MAX:
                        val_32 = SHRT_MAX
                    elif val_32 < SHRT_MIN:
                        val_32 = SHRT_MIN
                    val_32 = val_32 + <int>s2_16[i]
                    if val_32 > SHRT_MAX:
                        val_32 = SHRT_MAX
                    elif val_32 < SHRT_MIN:
                        val_32 = SHRT_MIN
                    out_16[i] = <short>val_32
            else:
                for i in range(num_samples):
                    val_32 = <int>out_16[i] + <int>s2_16[i]
                    if val_32 > SHRT_MAX:
                        val_32 = SHRT_MAX
                    elif val_32 < SHRT_MIN:
                        val_32 = SHRT_MIN
                    out_16[i] = <short>val_32

            current_position += chunk_len
            if remaining_times > 0:
                remaining_times -= 1

    elif sample_width == 4:
        while True:
            if remaining_times == 0:
                break
            if current_position >= seg1_len_after_pos:
                break

            remaining = seg1_len_after_pos - current_position
            chunk_len = remaining if remaining < seg2_len else seg2_len
            num_samples = chunk_len // 4

            out_32 = <int*>(out_buf + position + current_position)
            s2_32 = <const int*>seg2_ptr

            if apply_gain:
                for i in range(num_samples):
                    val_64 = <long long>(<double>out_32[i] * db_factor)
                    if val_64 > INT_MAX:
                        val_64 = INT_MAX
                    elif val_64 < INT_MIN:
                        val_64 = INT_MIN
                    val_64 = val_64 + <long long>s2_32[i]
                    if val_64 > INT_MAX:
                        val_64 = INT_MAX
                    elif val_64 < INT_MIN:
                        val_64 = INT_MIN
                    out_32[i] = <int>val_64
            else:
                for i in range(num_samples):
                    val_64 = <long long>out_32[i] + <long long>s2_32[i]
                    if val_64 > INT_MAX:
                        val_64 = INT_MAX
                    elif val_64 < INT_MIN:
                        val_64 = INT_MIN
                    out_32[i] = <int>val_64

            current_position += chunk_len
            if remaining_times > 0:
                remaining_times -= 1

    else:
        while True:
            if remaining_times == 0:
                break
            if current_position >= seg1_len_after_pos:
                break

            remaining = seg1_len_after_pos - current_position
            chunk_len = remaining if remaining < seg2_len else seg2_len

            seg1_slice = output_bytes[position + current_position:position + current_position + chunk_len]
            seg2_slice = seg2_data[:chunk_len]

            if apply_gain:
                seg1_slice = audioop.mul(seg1_slice, sample_width, db_factor)

            overlaid = audioop.add(seg1_slice, seg2_slice, sample_width)
            memcpy(out_buf + position + current_position, <const char*>overlaid, chunk_len)

            current_position += chunk_len
            if remaining_times > 0:
                remaining_times -= 1

    return output_bytes
