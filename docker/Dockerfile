# ============================================
# BUBBABAGS MARKETING INTELLIGENCE PLATFORM
# ============================================
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar uvicorn para API
RUN pip install uvicorn

# Copiar código fuente
COPY src/ ./src/
COPY ui/ ./ui/
COPY models/ ./models/

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Puertos
EXPOSE 8501 8002

# Comando por defecto: Streamlit
CMD ["streamlit", "run", "ui/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]