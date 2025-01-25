def test_note_repr(note1):
    # When
    result = repr(note1)

    # Then
    guid, front, back, tags = note1.guid, note1.front, note1.back, note1.tags
    assert (
        result
        == f"Note(guid='{guid}', front='{front}', back='{back}', tags={tags}, notetype=None, deck_name=None)"
    )
