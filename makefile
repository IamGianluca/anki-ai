install:
	uv sync --all-extras && \
	uv pip install -e . 

test:
	pytest . -m "not slow" --ignore=tests/integration/ --durations=5 --cov=src/anki_ai/ --cov-report term-missing -vv

test_slow:
	pytest . --durations=5 --cov=src/anki_ai/ --cov-report term-missing -vv

check: format lint

format:
	ruff format .

lint:
	ruff check --fix

jupyter:
	jupyter lab --ip 0.0.0.0 --no-browser --allow-root --port 8888

vllm:
	vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct --max_model_len 4096 --chat-template ./template_llama31.jinja
