import cython
import audioop

@cython.boundscheck(False)
@cython.wraparound(False)
def overlay_segments(
    bytes seg1_data,
    bytes seg2_data,
    int sample_width,
    int position,
    int times,
    int gain_during_overlay = 0
):
    cdef int seg1_len = len(seg1_data)
    cdef int seg2_len = len(seg2_data)
    cdef list output_middle
    cdef int remaining
    cdef bytes seg1_slice, seg2_slice, overlaid_slice
    cdef float db_factor = 1.0
    cdef int remaining_times = times
    cdef int current_position
    cdef int current_seg2_len

    if position >= seg1_len:
        return seg1_data

    apply_gain = gain_during_overlay != 0
    if apply_gain:
        db_factor = 10 ** (gain_during_overlay / 20.0)

    result_before = seg1_data[:position]

    seg1_data = seg1_data[position:]
    seg1_len = len(seg1_data)
    current_position = 0
    overlaid_slices = []
    while True:
        if remaining_times == 0:
            break

        if current_position >= seg1_len:
            break

        remaining = max(seg1_len - current_position, 0)
        current_seg2_len = remaining if remaining < seg2_len else seg2_len

        seg1_slice = seg1_data[current_position:current_position + current_seg2_len]
        seg2_slice = seg2_data[:current_seg2_len]

        if apply_gain:
            seg1_slice = audioop.mul(seg1_slice, sample_width, db_factor)

        overlaid_slice = audioop.add(seg1_slice, seg2_slice, sample_width)
        overlaid_slices.append(overlaid_slice)

        current_position += current_seg2_len

        if remaining_times > 0:
            remaining_times -= 1

    return result_before + b"".join(overlaid_slices) + seg1_data[current_position:]
