import asyncio

import uvicorn
from fastapi import FastAPI
from vllm import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.entrypoints.logger import RequestLogger
from vllm.entrypoints.openai.protocol import ChatCompletionRequest
from vllm.entrypoints.openai.serving_chat import OpenAIServingChat

MODEL_DIR = ["meta-llama/Meta-Llama-3.1-8B-Instruct"]


def serving_chat():
    model = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    max_model_len = 4_096
    # chat_template = "./template_llama31.jinja"
    engine_args = AsyncEngineArgs(model=model, max_model_len=max_model_len)
    engine = AsyncLLMEngine.from_engine_args(engine_args)

    model_config = asyncio.run(engine.get_model_config())
    serving_chat = OpenAIServingChat(
        engine,
        model_config=model_config,
        chat_template=None,
        served_model_names=MODEL_DIR,
        response_role="assistant",
        lora_modules=[],
        prompt_adapters=[],
        request_logger=RequestLogger(max_log_len=2048),
    )

    return serving_chat


def run_server():
    app = FastAPI()
    chat = serving_chat()

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatCompletionRequest):
        return await chat.create_chat_completion(request)

    uvicorn.run(app, host="0.0.0.0", port=8000)


# def start_live_server():
#     proc = multiprocessing.Process(target=run_server, args=(serving_chat,))
#     proc.start()
#     time.sleep(2)  # Give the server some time to start
#
#     yield "http://localhost:8000"
#
#     proc.terminate()
#     proc.join()


if __name__ == "__main__":
    run_server()
