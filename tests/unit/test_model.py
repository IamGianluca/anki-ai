import pytest
from anki_ai.domain.model import Deck, Note


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


def test_deck_from_txt(deck):
    # given
    assert len(deck) == 2  # the deck fixture comes with two notes already

    # when
    fpath = "./tests/data/test_data.txt"
    deck.from_txt(fpath)

    # then
    assert len(deck) == 10  # 2 existing + 8 in sample file


def test_deck_from_txt_ignore_media(deck):
    # given
    assert len(deck) == 2  # the deck fixture comes with two notes already

    # when
    fpath = "./tests/data/test_data.txt"
    deck.from_txt(fpath, ignore_media=False)

    # then
    assert len(deck) == 12  # 2 existing + 10 in sample file (2 include media content)


def test_deck_load_from_txt_verbose(capsys, deck):
    # when
    fpath = "./tests/data/test_data.txt"
    deck.from_txt(fpath, verbose=True)

    captured = capsys.readouterr()
    assert (
        captured.out
        == """Was not able to process line 0: #separator:tab

Was not able to process line 1: #html:true

Was not able to process line 2: #tags column:6

"""
    )
