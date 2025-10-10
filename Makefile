PYTHON=python3
PIP=$(PYTHON) -m pip
UVICORN=uvicorn

install:
	$(PIP) install -r requirements.txt

format:
	$(PYTHON) -m black app tests

lint:
	ruff check app tests

lint-fix:
	ruff check app tests --fix

format-check:
	$(PYTHON) -m black --check app tests

typecheck:
	$(PYTHON) -m mypy app

test:
	coverage run -m pytest
	coverage report

run:
	$(UVICORN) app.main:app --host 0.0.0.0 --port $${PORT:-8000}

dev: run

.PHONY: install format lint lint-fix format-check typecheck test run dev
