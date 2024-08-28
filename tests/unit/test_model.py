import pytest
from loguru import logger

from anki_ai.domain.model import Deck, Note


@pytest.fixture(scope="function")
def note1() -> Note:
    return Note(front="fake front", back="fake back", tags=["fake tag1"])


@pytest.fixture(scope="function")
def note2() -> Note:
    return Note(front="fake front", back="fake back", tags=["fake tag2"])


@pytest.fixture(scope="function")
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
    assert result == f"Note(uuid={uuid}, front={front}, back={back}, tags={tags}"


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
    "fpath,sep,html,ncols",
    [
        ("./tests/data/test_data.txt", "\t", True, 6),
        ("./tests/data/test_data_incl_.txt", "\t", False, 6),
    ],
)
def test_deck_parse_file_header(fpath, sep, html, ncols):
    # given
    deck = Deck("default")

    # when
    deck.read_txt(fpath)

    # then
    assert deck.sep_ == sep
    assert deck.html_ == html
    assert deck.tags_ncols_ == ncols


@pytest.mark.parametrize(
    argnames="ignore_media,result", argvalues=[(True, 10), (False, 12)]
)
def test_deck_read_txt_simple(deck, ignore_media, result):
    # given
    assert len(deck) == 2  # the deck fixture comes with two notes already

    # when
    fpath = "./tests/data/test_data.txt"
    deck.read_txt(fpath, ignore_media=ignore_media)

    # then
    assert len(deck) == result  # 2 existing + 8 non-media sample + 2 media samples


def test_deck_read_txt_more_fields(deck):
    # given
    assert len(deck) == 2

    # when
    fpath = "./tests/data/test_data_incl_.txt"
    deck.read_txt(fpath)

    # then
    assert len(deck) == 10


def test_deck_load_read_txt_logging(caplog, deck):
    # when
    fpath = "./tests/data/test_data.txt"
    deck.read_txt(fpath)

    # then
    assert caplog.text == ""
