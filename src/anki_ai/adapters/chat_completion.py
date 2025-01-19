import json
from typing import Any, Protocol

from openai import OpenAI
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage


class ChatCompletionsService(Protocol):
    def create(self, *args: Any, **kwargs: Any) -> Any:
        pass


class FakeCompletions:
    def create(self, model, messages, temperature=0.7, max_tokens=150, *args, **kwargs):
        fake_note = {
            "front": "This is the front of the card",
            "back": "This is the back of the card",
            "tags": ["tag1", "tag2"],
        }

        fake_response = json.dumps(fake_note)
        return FakeChatCompletion(
            id="chat-123",
            created=12523424,
            model=model,
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant", content=fake_response
                    ),
                    finish_reason="stop",
                )
            ],
            object="chat.completion",
        )


class FakeChatCompletion:
    def __init__(self, id, created, model, choices: list[Choice], object):
        self.id = id
        self.created = created
        self.model_name = model
        self.choices = choices
        self.object = object


def get_completion(nullable: bool = False):
    if nullable:
        return None  # TODO: implement
    else:
        client = get_vllm_client()
        return client.completions


def get_chat_completion(nullable: bool = False) -> ChatCompletionsService:
    if nullable:
        return FakeCompletions()
    else:
        client = get_vllm_client()
        return client.chat.completions


def get_vllm_client() -> OpenAI:
    OPENAI_API_KEY = "EMPTY"
    OPENAI_API_BASE = "http://localhost:8000/v1"
    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )
