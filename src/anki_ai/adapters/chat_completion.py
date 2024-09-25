import json
from typing import Any, Protocol

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage


class ChatCompletionService(Protocol):
    def create(self, *args: Any, **kwargs: Any) -> Any:
        pass


class FakeChatCompletion:
    def create(self, model, messages, temperature=0.7, max_tokens=150, *args, **kwargs):
        fake_note = {
            "front": "This is the front of the card",
            "back": "This is the back of the card",
            "tags": ["tag1", "tag2"],
        }

        response = json.dumps(fake_note)

        return ChatCompletion(
            id="chat-123",
            created=12523424,
            model="mymodel",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(role="assistant", content=response),
                    finish_reason="stop",
                )
            ],
            object="chat.completion",
        )


def get_chat_completion(nullable=False) -> ChatCompletionService:
    if nullable:
        return FakeChatCompletion()
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
