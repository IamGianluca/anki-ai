from typing import List

import pytest
from loguru import logger

from anki_ai.domain.deck import Deck
from anki_ai.domain.note import Note


@pytest.fixture
def note1() -> Note:
    return Note(
        guid="first",
        front="Front 1",
        back="Back 1",
        tags=["Tag1"],
        notetype="KaTeX and Markdown Basic (Color)",
        deck_name="Default",
    )


@pytest.fixture
def note2() -> Note:
    return Note(
        guid="second",
        front="Front 2",
        back="Back 2",
        tags=["Tag2"],
        notetype="KaTeX and Markdown Basic (Color)",
        deck_name="Default",
    )


@pytest.fixture
def note3() -> Note:
    return Note(
        guid="third",
        front="Front 3",
        back="Back 3",
        tags=["Tag3"],
        notetype="KaTeX and Markdown Basic (Color)",
        deck_name="Default",
    )


def create_fake_file_str(notes: List[Note]) -> str:
    header_str = "#separator:tab\n#html:true\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:9\n"
    notes_str = "\n".join([n.to_file_str() for n in notes])
    return header_str + notes_str


@pytest.fixture
def test_file(tmp_path, note1):
    file = tmp_path / "test_file.txt"
    file_content = create_fake_file_str(notes=[note1])
    file.write_text(file_content)
    return file


@pytest.fixture
def empty_deck():
    return Deck()


@pytest.fixture
def deck(note1, note2) -> Deck:
    deck = Deck()
    deck.add([note1, note2])
    return deck


@pytest.fixture
def caplog(caplog):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
