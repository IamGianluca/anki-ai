import json
from types import SimpleNamespace
from typing import Any, Protocol

from openai import OpenAI


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
                        content=response,
                    ),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(
                prompt_tokens=9, completion_tokens=12, total_tokens=21
            ),
        )


def get_chat_completion() -> ChatCompletionService:
    client = get_vllm_client()
    return client.chat.completions


def get_vllm_client() -> OpenAI:
    OPENAI_API_KEY = "EMPTY"
    OPENAI_API_BASE = "http://localhost:8000/v1"
    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )
