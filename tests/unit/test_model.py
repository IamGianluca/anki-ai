import pytest

from anki_ai.domain.model import Note

SIMPLE_FILE_FPATH = "./tests/data/test_data.txt"
COMPLEX_FILE_FPATH = "./tests/data/test_data_incl_.txt"


def test_read_from_fake_file(empty_deck, simple_file):
    empty_deck.read_txt(simple_file)
    assert len(empty_deck) > 0


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


def test_add_single_note(empty_deck):
    note = Note(front="Test Front", back="Test Back")
    empty_deck.add([note])
    assert len(empty_deck) == 1
    assert empty_deck[0] == note


def test_add_multiple_notes(empty_deck, note1, note2, note3):
    notes = [
        note1,
        note2,
        note3,
    ]
    empty_deck.add(notes)
    assert len(empty_deck) == 3
    assert empty_deck[:] == notes


def test_read_txt_with_invalid_separator(empty_deck, tmp_path):
    invalid_file = tmp_path / "invalid_separator.txt"
    invalid_file.write_text("#separator:comma\nfront,back,tags\n")

    with pytest.raises(
        NotImplementedError, match="Only tab-separated files are supported"
    ):
        empty_deck.read_txt(invalid_file)


def test_deck_iterable(deck):
    # when
    result = [note for note in deck]

    assert len(result) == 2


def test_read_txt_with_html_true(empty_deck, tmp_path):
    # given
    html_file = tmp_path / "html_true.txt"
    html_file.write_text(
        "#separator:tab\n#html:true\n<b>front</b>\t<i>back</i>\t\t\t\ttag1 tag2\n"
    )

    # when
    empty_deck.read_txt(html_file)

    # then
    assert len(empty_deck) == 1
    note = empty_deck[0]
    assert note.front == "<b>front</b>"
    assert note.back == "<i>back</i>"
    assert note.tags == ["tag1", "tag2"]


def test_read_txt_with_html_false(empty_deck, tmp_path):
    # given
    html_file = tmp_path / "html_false.txt"
    html_file.write_text("#separator:tab\n#html:false\nfront\tback\t\t\t\ttag1 tag2\n")

    # when
    empty_deck.read_txt(html_file)

    # then
    assert len(empty_deck) == 1
    note = empty_deck[0]
    assert note.front == "front"
    assert note.back == "back"
    assert note.tags == ["tag1", "tag2"]


def test_read_txt_with_deck_columns(empty_deck, tmp_path):
    # given
    deck_file = tmp_path / "deck_columns.txt"
    deck_file.write_text(
        "#separator:tab\n#deck columns:3\nuuid\tnote_type\tdeck_name\tfront\tback\ttags\n"
    )

    # when
    empty_deck.read_txt(deck_file)

    # then
    assert empty_deck.deck_ncols_ == 3


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


def test_deck_write_header(empty_deck, simple_file, tmp_path):
    # given
    empty_deck.read_txt(simple_file)

    # when
    fpath = tmp_path / "new.txt"
    empty_deck.write_txt(fpath)

    # then
    expected = ""
    with open(simple_file, "r") as f:
        for line in f.readlines():
            if line.startswith("#"):
                expected += line
            else:
                break

    result = ""
    with open(fpath, "r") as f:
        for line in f.readlines():
            if line.startswith("#"):
                result += line
            else:
                break
    assert expected == result
