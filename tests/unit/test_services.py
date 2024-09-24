from anki_ai.adapters.chat_completion import FakeChatCompletion
from anki_ai.domain.model import Note
from anki_ai.service_layer.services import format_note


def test_format_note(note1):
    result = format_note(note1, FakeChatCompletion())
    assert isinstance(result, Note)


def test_format_deck_cli():
    pass
