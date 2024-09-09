import pytest
from loguru import logger

from anki_ai.domain.model import Deck, Note


@pytest.fixture
def simple_file(tmp_path):
    file = tmp_path / "simple_file.txt"
    file.write_text(
        "#separator:tab\n#html:true\n<b>front</b>\t<i>back</i>\t\t\t\ttag1 tag2\n"
    )
    return file


@pytest.fixture
def note1() -> Note:
    return Note(front="Front 1", back="Back 1", tags=["Tag 1"])


@pytest.fixture
def note2() -> Note:
    return Note(front="Front 2", back="Back 2", tags=["Tag 2"])


@pytest.fixture
def note3() -> Note:
    return Note(front="Front 3", back="Back 3", tags=["Tag 3"])


@pytest.fixture
def empty_deck():
    return Deck("empty")


@pytest.fixture
def deck(note1, note2) -> Deck:
    deck = Deck("test")
    deck.add([note1, note2])
    return deck


@pytest.fixture
def caplog(caplog):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
