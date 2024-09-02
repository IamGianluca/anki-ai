import pytest
from loguru import logger

from anki_ai.domain.model import Deck, Note

SIMPLE_FILE_FPATH = "./tests/data/test_data.txt"
COMPLEX_FILE_FPATH = "./tests/data/test_data_incl_.txt"


@pytest.fixture
def note1() -> Note:
    return Note(front="fake front", back="fake back", tags=["fake tag1"])


@pytest.fixture
def note2() -> Note:
    return Note(front="fake front", back="fake back", tags=["fake tag2"])


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


def test_note_repr(note1):
    # when
    result = repr(note1)

    # then
    uuid, front, back, tags = note1.uuid, note1.front, note1.back, note1.tags
    assert (
        result
        == f"Note(front='{front}', back='{back}', tags={tags}, uuid={uuid}, note_type=None, deck_name=None)"
    )


def test_retrieve_element_from_deck(note1, deck):
    # when
    result = deck[0]

    # then
    assert result == note1


def test_retrieve_slice_from_deck(note1, note2, deck):
    # when
    result = deck[:2]

    # then
    assert result == [note1, note2]


def test_deck_length(deck):
    # when
    result = len(deck)

    # then
    assert result == 2


@pytest.mark.parametrize(
    argnames="ignore_media,result", argvalues=[(True, 10), (False, 12)]
)
def test_deck_read_txt_simple(deck, ignore_media, result):
    # given
    assert len(deck) == 2  # the deck fixture comes with two notes already

    # when
    deck.read_txt(SIMPLE_FILE_FPATH, ignore_media=ignore_media)

    # then
    assert len(deck) == result  # 2 existing + 8 non-media sample + 2 media samples


def test_deck_read_txt_more_fields(deck):
    # given
    assert len(deck) == 2

    # when
    deck.read_txt(COMPLEX_FILE_FPATH)

    # then
    assert len(deck) == 10

    # when
    result = deck[4]

    # then
    assert result.uuid == "Azd65{j+,q"
    assert result.note_type == "KaTeX and Markdown Basic"
    assert result.deck_name == "Default"
    assert result.front == "Command to create a soft link"
    assert result.back == "```bash $ ln -s <file_name> <link_name> ```"
    assert result.tags == ["linux"]


def test_deck_read_txt_logging(caplog, deck):
    # when
    deck.read_txt(SIMPLE_FILE_FPATH)

    # then
    assert caplog.text == ""
