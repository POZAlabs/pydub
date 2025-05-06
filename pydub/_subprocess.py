import subprocess
from typing import Self


class _PopenParams:
    def __init__(self, stdin: int | None = None, data: bytes | None = None):
        self.stdin = stdin
        self.data = data

    @classmethod
    def empty(cls) -> Self:
        return cls()

    @classmethod
    def pipe(cls, stdin_bytes: bytes) -> Self:
        return cls(stdin=subprocess.PIPE, data=stdin_bytes)


class _ConversionCommand(list[str]):
    converter: str

    @classmethod
    def init(cls, converter: str) -> Self:
        result = cls([converter, "-y"])
        result.converter = converter
        return result

    def with_format(self, file_format: str) -> Self:
        self.extend(["-f", file_format])
        return self

    def with_codec(self, codec: str) -> Self:
        self.extend(["-acodec", codec])
        return self

    def with_filename(self, filename: str) -> Self:
        self.extend(["-i", filename])
        return self

    def without_filename(self, read_ahead_limit: int) -> Self:
        if self.converter == "ffmpeg":
            self.extend(
                [
                    "-read_ahead_limit",
                    str(read_ahead_limit),
                    "-i",
                    "cache:pipe:0",
                ]
            )
            return self

        self.extend(["-i", "-"])
        return self

    def remove_video(self) -> Self:
        self.extend(["-vn"])
        return self

    def with_start_second(self, start_second: int) -> Self:
        self.extend(["-ss", str(start_second)])
        return self

    def with_duration(self, duration: int) -> Self:
        self.extend(["-t", str(duration)])
        return self

    def from_stdin(self) -> Self:
        self.append("-")
        return self

    def with_parameters(self, parameters: list[str]) -> Self:
        self.extend(parameters)
        return self
