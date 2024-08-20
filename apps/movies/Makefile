VENV ?= .venv

init:
	python3.12 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

up:
	docker compose up --build

down:
	docker compose down -v --remove-orphans

plint:
	ruff format .
	ruff check . --fix --show-fixes
