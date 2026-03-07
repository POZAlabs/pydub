from pathlib import Path

import pytest

from pydub import AudioSegment

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@pytest.fixture
def drums1():
    path = DATA_DIR / "drums1.wav"
    if not path.exists():
        pytest.skip(f"{path} not found")
    return AudioSegment.from_file(path)


@pytest.fixture
def bass1():
    path = DATA_DIR / "bass1.wav"
    if not path.exists():
        pytest.skip(f"{path} not found")
    return AudioSegment.from_file(path)
