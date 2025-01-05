import filecmp

import pytest

from anki_ai.domain.model import Deck, Note

TEST_DATA_FILE_FPATH = "./tests/data/test_data.txt"


def test_note_repr(note1):
    # When
    result = repr(note1)

    # Then
    guid, front, back, tags = note1.guid, note1.front, note1.back, note1.tags
    assert (
        result
        == f"Note(guid='{guid}', front='{front}', back='{back}', tags={tags}, notetype=None, deck_name=None)"
    )


def test_add_one_note(empty_deck):
    # Given
    note = Note(guid="fake", front="Test Front", back="Test Back")

    # When
    empty_deck.add([note])

    # Then
    assert len(empty_deck) == 1
    assert empty_deck[0] == note


def test_add_multiple_notes(empty_deck, note1, note2, note3):
    # Given
    notes = [
        note1,
        note2,
        note3,
    ]

    # When
    empty_deck.add(notes)

    # Then
    assert len(empty_deck) == 3
    assert empty_deck[:] == notes


def test_deck_length(deck):
    # When
    result = len(deck)

    # Then
    assert result == 2


def test_retrieve_element_from_deck(note1, deck):
    # When
    result = deck[0]

    # Then
    assert result == note1


def test_retrieve_note_from_deck_by_guid():
    # Given
    deck = Deck()
    note = Note(guid="teuha", front="front", back="back")
    another_note = Note(guid="etuha234241ueuo", front="front", back="back")
    deck.add([another_note, note])

    # When
    result = deck.get(guid="teuha")

    # Then
    assert [note] == result


def test_retrieve_slice_from_deck(note1, note2, deck):
    # When
    result = deck[:2]

    # Then
    assert result == [note1, note2]


def test_read_from_fake_file(empty_deck, test_file):
    # When
    empty_deck.read_txt(test_file)

    # Then
    assert len(empty_deck) > 0


def test_read_txt_with_invalid_separator(empty_deck, tmp_path):
    # Given
    invalid_file = tmp_path / "invalid_separator.txt"
    invalid_file.write_text("#separator:comma\nfront,back,tags\n")

    # When / then
    with pytest.raises(
        NotImplementedError, match="Only tab-separated files are supported"
    ):
        empty_deck.read_txt(invalid_file)


def test_deck_iterable(deck):
    # When
    result = [note for note in deck]

    # Then
    assert len(result) == 2


def test_read_txt_with_html_true(empty_deck, tmp_path):
    # Given
    html_file = tmp_path / "html_true.txt"
    html_file.write_text(
        "#separator:tab\n#html:true\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:6\nMm+g*FhiWM\tKaTeX and Markdown Basic\tDefault\t<b>front</b>\t<i>back</i>\t\t\t\ttag1 tag2\n"
    )

    # When
    empty_deck.read_txt(html_file)

    # Then
    assert len(empty_deck) == 1
    note = empty_deck[0]
    assert note.front == "<b>front</b>"
    assert note.back == "<i>back</i>"
    assert note.tags == ["tag1", "tag2"]


def test_read_txt_with_html_false(empty_deck, tmp_path):
    # Given
    html_file = tmp_path / "html_false.txt"
    html_file.write_text(
        "#separator:tab\n#html:false\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:6\nMm+g*FhiWM\tKaTeX and Markdown Basic\tDefault\tfront\tback\t\t\t\ttag1 tag2\n"
    )

    # When
    empty_deck.read_txt(html_file)

    # Then
    assert len(empty_deck) == 1
    note = empty_deck[0]
    assert note.front == "front"
    assert note.back == "back"
    assert note.tags == ["tag1", "tag2"]


def test_deck_read_txt_more_fields(deck):
    # Given
    assert len(deck) == 2

    # When
    deck.read_txt(TEST_DATA_FILE_FPATH)

    # Then
    assert len(deck) == 10

    # When
    result = deck[4]

    # Then
    assert result.guid == "Azd65{j+,q"
    assert result.notetype == "KaTeX and Markdown Basic"
    assert result.deck_name == "Default"
    assert result.front == "Command to create a soft link"
    assert result.back == "```bash $ ln -s <file_name> <link_name> ```"
    assert result.tags == ["linux"]


def test_deck_read_txt_log_warnings(caplog, tmp_path, deck):
    # Given
    invalid_file = tmp_path / "invalid_file.txt"  # Missing two tabs before tags
    invalid_file.write_text("#separator:tab\n#html:false\nfront\tback\t\ttag1 tag2\n")

    # When
    deck.read_txt(invalid_file)

    # Then
    assert [r.levelname for r in caplog.records] == ["WARNING"]


def test_deck_write_txt(test_file, tmp_path):
    # Given
    deck = Deck("Default")
    deck.read_txt(test_file)

    # When
    out_fpath = tmp_path / "new.txt"
    deck.write_txt(out_fpath)

    # Then
    assert filecmp.cmp(test_file, out_fpath)


def test_update_note_in_deck():
    # Given
    note = Note(guid="guid", front="front", back="back")
    deck = Deck()
    deck.add([note])

    # When
    new_note = Note(guid="guid", front="new front", back="new back")
    deck.update(guid="guid", changes=new_note)

    # Then
    assert len(deck) == 1
    assert deck.get(guid="guid") == [new_note]
