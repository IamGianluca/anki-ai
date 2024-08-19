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
