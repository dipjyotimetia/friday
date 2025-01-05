.PHONY: install test lint run format

install:
    poetry install
    poetry shell

test:
    poetry run pytest

lint:
    ruff format

format:
    poetry run black .

run:
    poetry run python main.py