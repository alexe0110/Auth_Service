CODE ?= .
VENV ?= .venv

.PHONY: up down lint

init:
	python3.12 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

up:
	docker compose up redis postgres -d --build

down:
	docker compose down -v --remove-orphans

plint:
	ruff format $(CODE)
	ruff check $(CODE) --fix --show-fixes

