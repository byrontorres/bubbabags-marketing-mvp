.PHONY: install run-api run-ui demo train test lint clean

PYTHON = python
VENV = .venv
PIP = $(VENV)/Scripts/pip
PYTHON_VENV = $(VENV)/Scripts/python

setup-venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: setup-venv
	$(PIP) install -r requirements.txt

setup-views:
	$(PYTHON_VENV) scripts/setup_views.py

train:
	$(PYTHON_VENV) scripts/train_model.py

run-api:
	$(PYTHON_VENV) -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	$(PYTHON_VENV) -m streamlit run ui/app.py --server.port 8501

demo:
	docker-compose -f docker/docker-compose.yml up --build

test:
	$(PYTHON_VENV) -m pytest tests/ -v --cov=src

lint:
	$(PYTHON_VENV) -m ruff check src/ tests/ --fix

clean:
	if exist __pycache__ rmdir /s /q __pycache__
	if exist .pytest_cache rmdir /s /q .pytest_cache
