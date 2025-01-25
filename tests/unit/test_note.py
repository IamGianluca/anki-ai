def test_note_repr(note1):
    # When
    result = repr(note1)

    # Then
    guid, front, back, tags, notetype, deck_name = (
        note1.guid,
        note1.front,
        note1.back,
        note1.tags,
        note1.notetype,
        note1.deck_name,
    )
    assert (
        result
        == f"Note(guid='{guid}', front='{front}', back='{back}', tags={tags}, notetype='{notetype}', deck_name='{deck_name}')"
    )
