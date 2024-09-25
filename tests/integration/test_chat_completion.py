import pytest
from openai.types.chat.chat_completion import ChatCompletion

from anki_ai.adapters.chat_completion import get_chat_completion


@pytest.mark.parametrize("nullable", [True, False])
def test_chat_completion(nullable):
    # given
    chat = get_chat_completion(nullable=nullable)
    model = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    messages = [
        {"role": "system", "content": "Answer in Italian"},
        {"role": "user", "content": "Hello"},
    ]

    # when
    result = chat.create(
        model=model,
        messages=messages,  # type: ignore
        temperature=0,
    )

    # then
    assert isinstance(result, ChatCompletion)
    assert isinstance(result.choices[0].message.content, str)
