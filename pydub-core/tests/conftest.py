from pathlib import Path

import pytest

from pydub import AudioSegment

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@pytest.fixture
def drums1():
    return AudioSegment.from_file(DATA_DIR / "drums1.wav")


@pytest.fixture
def bass1():
    return AudioSegment.from_file(DATA_DIR / "bass1.wav")
