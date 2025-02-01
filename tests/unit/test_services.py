from anki_ai.adapters.chat_completion import get_chat_completion
from anki_ai.domain.note import Note
from anki_ai.service_layer.services import format_note


def test_format_note(note1):
    # Given
    llm = get_chat_completion(nullable=True)

    # When
    result = format_note(note1, llm)

    # Then
    assert isinstance(result, Note)


def test_format_note_does_not_overwrite_original_object(note1):
    # Given
    llm = get_chat_completion(nullable=True)

    # When
    result = format_note(note1, llm)

    # Then
    assert result.guid == note1.guid
    assert result != note1
