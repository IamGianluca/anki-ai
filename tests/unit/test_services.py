import json
from types import SimpleNamespace

from anki_ai.domain.model import Note
from anki_ai.service_layer.services import format_note


class FakeChatCompletion:
    def create(self, model, messages, temperature=0.7, max_tokens=150, *args, **kwargs):
        fake_note = {
            "front": "This is the front of the card",
            "back": "This is the back of the card",
            "tags": ["tag1", "tag2"],
        }

        response = json.dumps(fake_note)

        return SimpleNamespace(
            id="chatcmpl-123",
            object="chat.completion",
            created=1684888617,
            model=model,
            choices=[
                SimpleNamespace(
                    index=0,
                    message=SimpleNamespace(
                        role="assistant",
                        content=response,  # This is now a valid JSON string
                    ),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(
                prompt_tokens=9, completion_tokens=12, total_tokens=21
            ),
        )


def test_format_note(note1):
    result = format_note(note1, FakeChatCompletion())
    assert isinstance(result, Note)


def test_format_deck_cli():
    pass
