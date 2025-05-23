import functools
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile as _tempfile
import warnings
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

FRAME_WIDTHS = {
    8: 1,
    16: 2,
    32: 4,
}
ARRAY_TYPES = {
    8: "b",
    16: "h",
    32: "i",
}
ARRAY_RANGES = {
    8: (-0x80, 0x7F),
    16: (-0x8000, 0x7FFF),
    32: (-0x80000000, 0x7FFFFFFF),
}


def get_frame_width(bit_depth):
    return FRAME_WIDTHS[bit_depth]


def get_array_type(bit_depth, signed=True):
    t = ARRAY_TYPES[bit_depth]
    if not signed:
        t = t.upper()
    return t


def get_min_max_value(bit_depth):
    return ARRAY_RANGES[bit_depth]


def _fd_or_path_or_tempfile(fd, mode="w+b", tempfile=True):
    close_fd = False
    if fd is None and tempfile:
        fd = _tempfile.TemporaryFile(mode=mode)
        close_fd = True

    if isinstance(fd, str):
        fd = open(fd, mode=mode)
        close_fd = True

    if isinstance(fd, io.BufferedReader):
        close_fd = True

    try:
        if isinstance(fd, os.PathLike):
            fd = open(fd, mode=mode)
            close_fd = True
    except AttributeError:
        # module os has no attribute PathLike, so we're on python < 3.6.
        # The protocol we're trying to support doesn't exist, so just pass.
        pass

    return fd, close_fd


def db_to_float(db, using_amplitude=True):
    """
    Converts the input db to a float, which represents the equivalent
    ratio in power.
    """
    db = float(db)
    if using_amplitude:
        return 10 ** (db / 20)
    else:  # using power
        return 10 ** (db / 10)


def ratio_to_db(ratio, val2=None, using_amplitude=True):
    """
    Converts the input float to db, which represents the equivalent
    to the ratio in power represented by the multiplier passed in.
    """
    ratio = float(ratio)

    # accept 2 values and use the ratio of val1 to val2
    if val2 is not None:
        ratio = ratio / val2

    # special case for multiply-by-zero (convert to silence)
    if ratio == 0:
        return -float("inf")

    if using_amplitude:
        return 20 * math.log(ratio, 10)
    else:  # using power
        return 10 * math.log(ratio, 10)


def register_pydub_effect(fn, name=None):
    """
    decorator for adding pydub effects to the AudioSegment objects.
    example use:
        @register_pydub_effect
        def normalize(audio_segment):
            ...
    or you can specify a name:
        @register_pydub_effect("normalize")
        def normalize_audio_segment(audio_segment):
            ...
    """
    if isinstance(fn, str):
        name = fn
        return lambda fn: register_pydub_effect(fn, name)

    if name is None:
        name = fn.__name__

    from .audio_segment import AudioSegment

    setattr(AudioSegment, name, fn)
    return fn


def make_chunks(audio_segment, chunk_length):
    """
    Breaks an AudioSegment into chunks that are <chunk_length> milliseconds
    long.
    if chunk_length is 50 then you'll get a list of 50 millisecond long audio
    segments back (except the last one, which can be shorter)
    """
    number_of_chunks = math.ceil(len(audio_segment) / float(chunk_length))
    return [
        audio_segment[i * chunk_length : (i + 1) * chunk_length]
        for i in range(int(number_of_chunks))
    ]


def get_encoder_name():
    """
    Return enconder default application for system, either avconv or ffmpeg
    """
    if shutil.which("avconv") is not None:
        return "avconv"
    elif shutil.which("ffmpeg") is not None:
        return "ffmpeg"
    else:
        # should raise exception
        warnings.warn(
            "Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work",
            RuntimeWarning,
        )
        return "ffmpeg"


def get_player_name():
    """
    Return enconder default application for system, either avconv or ffmpeg
    """
    if shutil.which("avplay"):
        return "avplay"
    elif shutil.which("ffplay"):
        return "ffplay"
    else:
        # should raise exception
        warnings.warn(
            "Couldn't find ffplay or avplay - defaulting to ffplay, but may not work",
            RuntimeWarning,
        )
        return "ffplay"


def get_prober_name():
    """
    Return probe application, either avconv or ffmpeg
    """
    if shutil.which("avprobe"):
        return "avprobe"
    elif shutil.which("ffprobe"):
        return "ffprobe"
    else:
        # should raise exception
        warnings.warn(
            "Couldn't find ffprobe or avprobe - defaulting to ffprobe, but may not work",
            RuntimeWarning,
        )
        return "ffprobe"


def get_extra_info(stderr):
    """
    avprobe sometimes gives more information on stderr than
    on the json output. The information has to be extracted
    from stderr of the format of:
    '    Stream #0:0: Audio: flac, 88200 Hz, stereo, s32 (24 bit)'
    or (macOS version):
    '    Stream #0:0: Audio: vorbis'
    '      44100 Hz, stereo, fltp, 320 kb/s'

    :type stderr: str
    :rtype: list of dict
    """
    extra_info = {}

    re_stream = r"(?P<space_start> +)Stream #0[:\.](?P<stream_id>([0-9]+))(?P<content_0>.+)\n?(?! *Stream)((?P<space_end> +)(?P<content_1>.+))?"
    for i in re.finditer(re_stream, stderr):
        if i.group("space_end") is not None and len(i.group("space_start")) <= len(
            i.group("space_end")
        ):
            content_line = ",".join([i.group("content_0"), i.group("content_1")])
        else:
            content_line = i.group("content_0")
        tokens = [x.strip() for x in re.split("[:,]", content_line) if x]
        extra_info[int(i.group("stream_id"))] = tokens
    return extra_info


def mediainfo_json(filepath, read_ahead_limit=-1):
    """Return json dictionary with media info(codec, duration, size, bitrate...) from filepath"""
    prober = get_prober_name()
    command_args = [
        "-v",
        "info",
        "-show_format",
        "-show_streams",
    ]
    try:
        command_args += [os.fsdecode(filepath)]
        stdin_parameter = None
        stdin_data = None
    except TypeError:
        if prober == "ffprobe":
            command_args += ["-read_ahead_limit", str(read_ahead_limit), "cache:pipe:0"]
        else:
            command_args += ["-"]
        stdin_parameter = subprocess.PIPE
        file, close_file = _fd_or_path_or_tempfile(filepath, "rb", tempfile=False)
        file.seek(0)
        stdin_data = file.read()
        if close_file:
            file.close()

    command = [prober, "-of", "json"] + command_args
    res = subprocess.Popen(
        command, stdin=stdin_parameter, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, stderr = res.communicate(input=stdin_data)
    output = output.decode("utf-8", "ignore")
    stderr = stderr.decode("utf-8", "ignore")

    try:
        info = json.loads(output)
    except json.decoder.JSONDecodeError:
        # If ffprobe didn't give any information, just return it
        # (for example, because the file doesn't exist)
        return None
    if not info:
        return info

    extra_info = get_extra_info(stderr)

    audio_streams = [x for x in info["streams"] if x["codec_type"] == "audio"]
    if len(audio_streams) == 0:
        return info

    # We just operate on the first audio stream in case there are more
    stream = audio_streams[0]

    def set_property(stream, prop, value):
        if prop not in stream or stream[prop] == 0:
            stream[prop] = value

    for token in extra_info[stream["index"]]:
        m = re.match(r"([su]([0-9]{1,2})p?) \(([0-9]{1,2}) bit\)$", token)
        m2 = re.match(r"([su]([0-9]{1,2})p?)( \(default\))?$", token)
        if m:
            set_property(stream, "sample_fmt", m.group(1))
            set_property(stream, "bits_per_sample", int(m.group(2)))
            set_property(stream, "bits_per_raw_sample", int(m.group(3)))
        elif m2:
            set_property(stream, "sample_fmt", m2.group(1))
            set_property(stream, "bits_per_sample", int(m2.group(2)))
            set_property(stream, "bits_per_raw_sample", int(m2.group(2)))
        elif re.match(r"(flt)p?( \(default\))?$", token):
            set_property(stream, "sample_fmt", token)
            set_property(stream, "bits_per_sample", 32)
            set_property(stream, "bits_per_raw_sample", 32)
        elif re.match(r"(dbl)p?( \(default\))?$", token):
            set_property(stream, "sample_fmt", token)
            set_property(stream, "bits_per_sample", 64)
            set_property(stream, "bits_per_raw_sample", 64)
    return info


def mediainfo(filepath):
    """Return dictionary with media info(codec, duration, size, bitrate...) from filepath"""

    prober = get_prober_name()
    command_args = ["-v", "quiet", "-show_format", "-show_streams", filepath]

    command = [prober, "-of", "old"] + command_args
    res = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = res.communicate()[0].decode("utf-8")

    if res.returncode != 0:
        command = [prober] + command_args
        output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0].decode("utf-8")

    rgx = re.compile(r"(?:(?P<inner_dict>.*?):)?(?P<key>.*?)\=(?P<value>.*?)$")
    info = {}

    if sys.platform == "win32":
        output = output.replace("\r", "")

    for line in output.split("\n"):
        # print(line)
        mobj = rgx.match(line)

        if mobj:
            # print(mobj.groups())
            inner_dict, key, value = mobj.groups()

            if inner_dict:
                try:
                    info[inner_dict]
                except KeyError:
                    info[inner_dict] = {}
                info[inner_dict][key] = value
            else:
                info[key] = value

    return info


def cache_codecs(function):
    cache = {}

    @functools.wraps(function)
    def wrapper():
        try:
            return cache[0]
        except Exception:
            cache[0] = function()
            return cache[0]

    return wrapper


@cache_codecs
def get_supported_codecs():
    encoder = get_encoder_name()
    command = [encoder, "-codecs"]
    res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = res.communicate()[0].decode("utf-8")
    if res.returncode != 0:
        return []

    if sys.platform == "win32":
        output = output.replace("\r", "")

    rgx = re.compile(r"^([D.][E.][AVS.][I.][L.][S.]) (\w*) +(.*)")
    decoders = set()
    encoders = set()
    for line in output.split("\n"):
        match = rgx.match(line.strip())
        if not match:
            continue
        flags, codec, name = match.groups()

        if flags[0] == "D":
            decoders.add(codec)

        if flags[1] == "E":
            encoders.add(codec)

    return decoders, encoders


def get_supported_decoders():
    return get_supported_codecs()[0]


def get_supported_encoders():
    return get_supported_codecs()[1]


def stereo_to_ms(audio_segment):
    """
    Left-Right -> Mid-Side
    """
    from .audio_segment import AudioSegment

    channel = audio_segment.split_to_mono()
    channel = [channel[0].overlay(channel[1]), channel[0].overlay(channel[1].invert_phase())]
    return AudioSegment.from_mono_audiosegments(channel[0], channel[1])


def ms_to_stereo(audio_segment):
    """
    Mid-Side -> Left-Right
    """
    from .audio_segment import AudioSegment

    channel = audio_segment.split_to_mono()
    channel = [
        channel[0].overlay(channel[1]) - 3,
        channel[0].overlay(channel[1].invert_phase()) - 3,
    ]
    return AudioSegment.from_mono_audiosegments(channel[0], channel[1])


P = ParamSpec("P")
T = TypeVar("T")


def create_extra_required(module: Any | None, message: str) -> Callable[[Callable[P, T]], T]:
    def decorator(func: Callable[P, T]) -> T:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if module is None:
                raise ImportError(message)

            return func(*args, **kwargs)

        return wrapper

    return decorator
