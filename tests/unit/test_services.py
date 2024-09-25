from anki_ai.adapters.chat_completion import get_chat_completion
from anki_ai.domain.model import Note
from anki_ai.service_layer.services import format_note


def test_format_note(note1):
    # given
    chat = get_chat_completion(nullable=True)

    # when
    result = format_note(note1, chat)

    # then
    assert isinstance(result, Note)
