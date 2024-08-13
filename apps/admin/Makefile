CODE ?= .
VENV ?= .venv

.PHONY: up down lint

init:
	python3.12 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

run:
	$(VENV)/bin/python manage.py runserver

plint:
	ruff format $(CODE)
	ruff check $(CODE) --fix --show-fixes

