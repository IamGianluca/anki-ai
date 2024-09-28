import pytest
from openai.types.chat.chat_completion import ChatCompletion

from anki_ai.adapters.chat_completion import get_chat_completion

# We are running this test both against a real vLLM API server (nullable=False)
# and with the nullable. The goal is to ensure our stub behaves like the
# original third-party dependency.


@pytest.mark.parametrize("nullable", [True, False])
def test_chat_completion(nullable):
    # TODO(grossi): Create fixture to spin us real vLLM API server for real
    # integration test.

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
