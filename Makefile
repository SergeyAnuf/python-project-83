PORT ?= 8000

build:
		./build.sh

install:
		uv sync

render-start:
		.venv/bin/python -m gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app


start:
		uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app


lint:
		uv run ruff check

lint-fix:
		uv run ruff check --fix

dev:
		uv run flask --debug --app page_analyzer:app run