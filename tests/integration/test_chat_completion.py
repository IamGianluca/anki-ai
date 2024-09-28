import time
from multiprocessing import Process

import pytest
import requests
from openai.types.chat.chat_completion import ChatCompletion

from anki_ai.adapters.chat_completion import get_chat_completion
from anki_ai.entrypoints.api_server import run_server


@pytest.fixture(scope="module")
def vllm_server():
    """Spin up a real vLLM OpenAI compatible server that can be used for
    testing against the real dependency on narrow integration tests.

    Beware it takes about 20 seconds to be up and running.
    """
    # TODO(grossi): We could reduce the time it takes to spin up the server
    # by loading a smaller model (e.g., facebook/opt-125m). At the moment,
    # we are loading the same model we use in production
    # (i.e., meta-llama/Meta-Llama-3.1-8B-Instruct)
    process = Process(target=run_server)
    process.start()

    # Wait for server to become available
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            requests.head("http://localhost:8000/v1/chat/completions")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(3)
            attempt += 1
    else:
        pytest.fail("Server failed to start")

    yield

    process.terminate()
    process.join()


def test_vllm_server_chat_completions(vllm_server):
    # given
    url = "http://localhost:8000/v1/chat/completions"
    request_data = {
        "model": "llama-3b",
        "messages": [
            {
                "role": "user",
                "content": "Write a short story about a character who discovers a hidden world.",
            }
        ],
        "max_tokens": 256,
        "temperature": 1.0,
        "top_p": 1.0,
        "n": 1,
        "stream": False,
        "stop": None,
    }

    # when
    response = requests.post(url, json=request_data)

    # then
    assert response.status_code == 200


@pytest.mark.parametrize("nullable", [True, False])
def test_chat_completion(nullable, vllm_server):
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
