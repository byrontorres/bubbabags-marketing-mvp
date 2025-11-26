# Bubbabags Marketing Intelligence MVP

Agente conversacional de marketing con prediccion de ROAS sobre BigQuery.

## Quick Start

`ash
# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
copy .env.example .env

# Ejecutar demo
python scripts/run_demo.py
`

## Estructura

- src/data/ - Conexion BigQuery y queries
- src/analytics/ - Metricas y servicios
- src/modeling/ - Modelo ML de ROAS
- src/agent/ - Agente conversacional
- src/api/ - FastAPI endpoints
- ui/ - Streamlit app

## Comandos

- make install - Instala dependencias
- make train - Entrena modelo ROAS
- make run-api - Levanta FastAPI
- make run-ui - Levanta Streamlit
- make demo - Levanta todo con Docker
