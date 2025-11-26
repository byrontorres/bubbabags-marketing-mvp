.PHONY: install train run-ui demo clean

PYTHON = python
VENV = .venv
PIP = $(VENV)/Scripts/pip
PYTHON_VENV = $(VENV)/Scripts/python

# ============================================
# INSTALACIÓN
# ============================================
setup-venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: setup-venv
	$(PIP) install -r requirements.txt

# ============================================
# ENTRENAMIENTO DEL MODELO
# ============================================
train:
	$(PYTHON_VENV) scripts/train_model.py

# ============================================
# EJECUTAR INTERFAZ
# ============================================
run-ui:
	$(PYTHON_VENV) -m streamlit run ui/app.py --server.port 8501

# ============================================
# DOCKER
# ============================================
demo:
	docker-compose -f docker/docker-compose.yml up --build

# ============================================
# LIMPIEZA
# ============================================
clean:
	if exist __pycache__ rmdir /s /q __pycache__
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist src\__pycache__ rmdir /s /q src\__pycache__