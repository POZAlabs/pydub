import abc

from ..audio_segment import AudioSegment
from . import command


class ProcessAudio(abc.ABC):
    def __call__(self, cmd: command.ProcessAudioCommand) -> AudioSegment:
        return self.process(cmd)

    @abc.abstractmethod
    def process(self, cmd: command.ProcessAudioCommand) -> AudioSegment:
        raise NotImplementedError


class MergeAudio(ProcessAudio):
    def process(self, cmd: command.MergeAudioCommand) -> AudioSegment:
        result = cmd.to
        overlay_options = cmd.input.options.to_overlay_options(len(result))

        for opt in overlay_options:
            result = result.overlay(cmd.input.audio, **opt)

        return result


class MergeAudios(ProcessAudio):
    def process(self, cmd: command.MergeAudiosCommand) -> AudioSegment:
        overlay_policy = cmd.policy
        inputs = sorted(cmd.inputs, key=lambda x: overlay_policy.sort_key(x.audio))

        first, *rest = inputs
        result = first.audio
        for inp in rest:
            result = MergeAudio()(command.MergeAudioCommand(to=result, input=inp))

        return result


class ConvertAudio(ProcessAudio):
    def process(self, cmd: command.ConvertAudioCommand) -> AudioSegment:
        audio = cmd.audio
        result = audio.export(**cmd.options.to_options())
        return AudioSegment.from_file(result, format=cmd.options.format)
