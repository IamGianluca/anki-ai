import json
from typing import Any, Protocol

from openai import OpenAI
from openai.types import CompletionChoice
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage


# The OpenAI compatible server supports two modes: Completions and ChatCompletions
# (more precisely, a Completion object in the Chat module). The create method in
# each of these objects, return, respectively, a Completion and a ChatCompletion
# object. Note the missing "s" at the end.
class ChatCompletionsServiceProtocol(Protocol):
    def create(self, *args: Any, **kwargs: Any) -> Any:
        pass


class FakeCompletions:
    def create(self, model, prompt, temperature=0.7, max_tokens=150, *args, **kwargs):
        fake_note = {
            "front": "This is the front of the card",
            "back": "This is the back of the card",
            "tags": ["tag1", "tag2"],
        }

        fake_response = json.dumps(fake_note)
        return FakeCompletion(
            id="completion-123",
            created=12523424,
            model=model,
            choices=[
                CompletionChoice(index=0, text=fake_response, finish_reason="stop")
            ],
            object="completion",
        )


class FakeCompletion:
    def __init__(self, id, created, model, choices: list[CompletionChoice], object):
        self.id = id
        self.created = created
        self.model_name = model
        self.choices = choices
        self.object = object


class FakeChatCompletions:
    def create(self, model, messages, temperature=0.7, max_tokens=150, *args, **kwargs):
        # TODO: we should not create the fake note here
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


def get_completion(nullable: bool = False) -> ChatCompletionsServiceProtocol:
    if nullable:
        return FakeCompletions()
    else:
        client = get_vllm_client()
        return client.completions


def get_chat_completion(nullable: bool = False) -> ChatCompletionsServiceProtocol:
    if nullable:
        return FakeChatCompletions()
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
