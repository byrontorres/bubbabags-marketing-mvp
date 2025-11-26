# Bubbabags Marketing Intelligence Platform

Plataforma de análisis y predicción de campañas publicitarias para Google Ads y Meta Ads, con agente conversacional basado en LLM.

## Características

- **Análisis unificado** de Google Ads y Meta Ads desde BigQuery
- **Modelo predictivo XGBoost** para Google Ads (R² 0.684, +24.1% vs baseline)
- **Baseline histórico** para Meta Ads (R² 0.567)
- **Agente conversacional** con OpenAI GPT-4o-mini
- **Dashboard ejecutivo** con métricas en tiempo real
- **Docker** para deployment simplificado

## Métricas del Proyecto

| Canal | Modelo | R² | Mejora vs Baseline |
|-------|--------|----|--------------------|
| Google Ads | XGBoost | 0.684 | +24.1% |
| Meta Ads | Baseline histórico | 0.567 | N/A |

## Stack Tecnológico

- **Backend**: Python 3.12
- **ML**: XGBoost, scikit-learn, pandas
- **Data**: Google BigQuery
- **LLM**: OpenAI GPT-4o-mini
- **UI**: Streamlit
- **Deploy**: Docker

## Estructura del Proyecto
```
bubbabags-mvp/
├── src/
│   ├── config.py           # Configuración
│   ├── agent/agent.py      # Agente conversacional
│   ├── data/               # Conexión BigQuery
│   │   ├── bigquery_client.py
│   │   └── views.py
│   └── modeling/           # Modelos ML
│       ├── features.py
│       ├── train.py
│       └── predict.py
├── ui/app.py               # Interfaz Streamlit
├── models/                 # Modelos entrenados
├── docker/                 # Configuración Docker
├── scripts/                # Scripts de ejecución
└── requirements.txt
```

## Instalación

### Opción 1: Local
```bash
# 1. Clonar repositorio
git clone https://github.com/byrontorres/bubbabags-marketing-mvp.git
cd bubbabags-marketing-mvp

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Ejecutar
streamlit run ui/app.py
```

### Opción 2: Docker
```bash
# Requiere credenciales de Google Cloud configuradas
docker-compose -f docker/docker-compose.yml up --build
```

Acceder a: http://localhost:8501

## Configuración

Crear archivo `.env` con:
```env
# Google Cloud
GCP_PROJECT_ID=tu-proyecto
BQ_DATASET=tu-dataset

# OpenAI
OPENAI_API_KEY=sk-...
```

## Uso

### Consultas de ejemplo

- "¿Cuál canal tiene mejor ROAS?"
- "¿Cuál fue la mejor campaña?"
- "Compara Google Ads vs Meta Ads"
- "¿Qué campaña tendrá mejor rendimiento?"

### Scripts disponibles
```bash
# Entrenar modelo
python scripts/train_model.py

# Ejecutar interfaz
python scripts/run_ui.py
```

## Arquitectura
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│  Agente LLM     │────▶│   BigQuery      │
│   (UI)          │     │  (OpenAI)       │     │   (Datos)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Modelo ML      │
                        │  (XGBoost)      │
                        └─────────────────┘
```

## Capturas de Pantalla

### Dashboard Principal
- Métricas: Inversión, Revenue, ROAS, Campañas activas
- Chat conversacional con datos reales
- Comparativas por canal

### Modelos Predictivos
- Google Ads: XGBoost con R² 0.684
- Meta Ads: Baseline histórico con R² 0.567

## Autor

**Byron Torres** - Data Engineer

## Licencia

Este proyecto es privado y confidencial.