install:
	uv pip compile --all-extras pyproject.toml -o requirements.txt && \
	uv pip sync requirements.txt && \
	uv pip install -e . 

test:
	pytest . --durations=5 --cov=src/anki_ai/ --cov-report term-missing -vv

check: format lint

format:
	ruff format .

lint:
	ruff check --fix

jupyter:
	jupyter lab --ip 0.0.0.0 --no-browser --allow-root --port 8888
