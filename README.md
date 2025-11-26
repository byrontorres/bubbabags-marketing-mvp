# Bubbabags Marketing Intelligence Platform

Plataforma integral de inteligencia de marketing con ML, análisis conversacional y automatización mediante **n8n** para orquestación del bot de Telegram.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![BigQuery](https://img.shields.io/badge/BigQuery-Enabled-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![n8n](https://img.shields.io/badge/n8n-Automation-red)

---

## Tabla de Contenidos

- [Características](#-características)
- [Stack Tecnológico](#-stack-tecnológico)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Uso](#-uso)
  - [Bot de Telegram](#-bot-de-telegram)
  - [Interfaz Streamlit](#-interfaz-streamlit)
  - [API REST](#-api-rest)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Modelo de Machine Learning](#-modelo-de-machine-learning)
- [Configuración de n8n](#-configuración-de-n8n)
- [Variables de Entorno](#-variables-de-entorno)
- [Próximas Mejoras](#-próximas-mejoras)

---

## Características

### Core Features
- **Análisis de Campañas**: Métricas en tiempo real de Google Ads y Meta Ads
- **Predicción de ROAS**: Modelo XGBoost entrenado (R² 0.684, +24% vs baseline)
- **Agente Conversacional**: Responde preguntas en lenguaje natural con OpenAI
- **Bot de Telegram**: Automatizado 100% con **n8n** workflow engine
- **Dashboard Interactivo**: Visualización con Streamlit
- **API REST**: 6 endpoints para integración con sistemas externos

### Datos Procesados
- **49.2M** impresiones (Google Ads)
- **108.1M** impresiones (Meta Ads)
- **70 campañas** activas
- **Datos históricos** con análisis diario y mensual

---

## Stack Tecnológico

| Categoría | Tecnología | Versión | Propósito |
|-----------|------------|---------|-----------|
| **Backend** | Python | 3.12 | Core del sistema |
| **Base de Datos** | Google BigQuery | Cloud | Almacenamiento de datos |
| **ML/AI** | XGBoost | Latest | Modelo predictivo ROAS |
| **LLM** | OpenAI GPT-4o-mini | Latest | Agente conversacional |
| **API** | FastAPI | Latest | Backend API REST |
| **Frontend** | Streamlit | Latest | Dashboard interactivo |
| **Automation** | n8n | 1.121.2 | **Orquestación del bot de Telegram** |
| **Containerización** | Docker Compose | Latest | Despliegue de servicios |
| **Chat** | Telegram Bot API | Latest | Interfaz conversacional |

---

## Arquitectura
```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO FINAL                            │
└───────────┬─────────────────────┬───────────────────────────────┘
            │                     │
     ┌──────▼──────┐       ┌─────▼──────┐
     │  Telegram   │       │ Streamlit  │
     │    Bot      │       │     UI     │
     └──────┬──────┘       └─────┬──────┘
            │                    │
      ┌─────▼────────┐           │
      │     n8n      │           │
      │  Workflow    │           │
      │  Engine      │           │
      └─────┬────────┘           │
            │                    │
            └────────┬───────────┘
                     │
            ┌────────▼─────────┐
            │   FastAPI API    │
            │   (Puerto 8002)  │
            └────────┬─────────┘
                     │
        ┏━━━━━━━━━━━━┻━━━━━━━━━━━━┓
        ┃                          ┃
   ┌────▼─────┐            ┌──────▼──────┐
   │  OpenAI  │            │   BigQuery  │
   │  Agent   │            │    Views    │
   └────┬─────┘            └──────┬──────┘
        │                         │
   ┌────▼─────┐            ┌──────▼──────┐
   │ XGBoost  │            │  Google Ads │
   │  Model   │            │   Meta Ads  │
   └──────────┘            └─────────────┘
```

### Flujo de Datos - Bot de Telegram con n8n

1. **Usuario** → Envía mensaje a @bubbabags_mkt_bot
2. **n8n Workflow** → Captura mensaje cada 30 segundos
3. **n8n IF Node** → Filtra mensajes nuevos (anti-duplicados)
4. **n8n HTTP Request** → Llama a `/api/ask` con la pregunta
5. **Agente OpenAI** → Interpreta y ejecuta herramientas
6. **BigQuery + XGBoost** → Obtiene datos y predicciones
7. **n8n HTTP Request** → Envía respuesta al usuario vía Telegram

---

## Instalación

### Prerrequisitos

- Python 3.12+
- Docker & Docker Compose
- Cuenta de Google Cloud con BigQuery habilitado
- API Key de OpenAI
- Bot de Telegram (opcional, para usar la función de chatbot)

### 1. Clonar el repositorio
```bash
git clone https://github.com/byrontorres/bubbabags-marketing-mvp.git
cd bubbabags-marketing-mvp
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:
```env
# Google Cloud
GCP_PROJECT_ID=tu-proyecto-gcp
BQ_DATASET=marketing_analytics

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Telegram (opcional - solo si usas el bot)
TELEGRAM_BOT_TOKEN=tu-token-telegram
```

### 3. Autenticar con Google Cloud
```bash
gcloud auth application-default login
```

### 4. Levantar servicios con Docker
```bash
docker-compose -f docker/docker-compose.yml up --build -d
```

Esto levantará 3 servicios:
- **Streamlit** → http://localhost:8501
- **API FastAPI** → http://localhost:8002
- **n8n** → http://localhost:5678

---

## Uso

### Bot de Telegram

#### ¿Qué es n8n?

**n8n** es un workflow automation tool que orquesta todo el flujo del bot de Telegram:
- Consulta mensajes cada 30 segundos
- Filtra mensajes ya procesados
- Llama a la API de Bubbabags
- Envía respuestas de vuelta al usuario

Todo esto funciona **100% automático** sin intervención manual.

#### Acceso Directo
- **Username**: @bubbabags_mkt_bot
- **Link**: https://t.me/bubbabags_mkt_bot

#### Comandos y Preguntas

El bot responde en lenguaje natural. Ejemplos:
```
Usuario: "¿Cuál canal tiene mejor ROAS?"
Bot: Meta Ads tiene un ROAS promedio de 49.79x, 
       comparado con Google Ads que tiene 23.24x...

Usuario: "Dame las top 5 campañas"
Bot: Aquí están las 5 mejores campañas por ROAS:
       1. marzo | metrix | conversiones - ROAS: 260.55
       2. METRIX | PRODUCTOS Y OFERTAS - ROAS: 118.03
       ...

Usuario: "¿En qué campaña debería invertir hoy?"
Bot: Te recomiendo aumentar inversión en "marzo | metrix"
       con ROAS de 260.55, costo $94.87, revenue $22,631.80...
```

#### Tipos de Consultas Soportadas

Comparación de canales (Google Ads vs Meta Ads)  
- Top campañas por rendimiento  
- Predicciones de ROAS con ML  
- Evolución de KPIs (CTR, ROAS, costos)  
- Rendimiento mensual por campaña  
- Recomendaciones de inversión  

#### Características Técnicas

- **Tiempo de respuesta**: ~30 segundos (máximo)
- **Automatización**: n8n workflow ejecuta cada 30 segundos
- **IA**: GPT-4o-mini con function calling
- **Datos**: Consultas en tiempo real a BigQuery
- **Anti-duplicados**: Filtro temporal en n8n

---

### Interfaz Streamlit

#### Acceso
```
http://localhost:8501
```

#### Funcionalidades

**1. Chat Interactivo**
- Pregunta en lenguaje natural
- Respuestas con datos en tiempo real
- Historial de conversación

**2. Predictor de ROAS**
- Ingresar ID de campaña
- Definir presupuesto propuesto
- Obtener predicción de ROAS y revenue estimado

**3. Dashboard de Campañas**
- Visualización de métricas
- Filtros por fecha y canal
- Gráficos interactivos

---

### API REST

#### Base URL
```
http://localhost:8002
```

#### Endpoints Disponibles

##### 1. Health Check
```bash
GET /api/health
```

**Respuesta:**
```json
{
  "status": "healthy"
}
```

##### 2. Resumen por Canal
```bash
GET /api/channel-summary
```

**Respuesta:**
```json
{
  "status": "success",
  "data": [
    {
      "channel": "google_ads",
      "total_campaigns": 9,
      "total_impressions": 49208540,
      "avg_roas": 23.24
    },
    {
      "channel": "meta_ads",
      "total_campaigns": 61,
      "total_impressions": 108123311,
      "avg_roas": 49.79
    }
  ]
}
```

##### 3. Top Campañas
```bash
GET /api/top-campaigns?limit=5
```

**Parámetros:**
- `limit` (int, opcional): Número de campañas a retornar (default: 5)

##### 4. Resumen de Predicciones
```bash
GET /api/prediction-summary
```

##### 5. Agente Conversacional
```bash
POST /api/ask
Content-Type: application/json

{
  "question": "¿Cuál canal tiene mejor ROAS?"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "question": "¿Cuál canal tiene mejor ROAS?",
  "answer": "Meta Ads tiene un ROAS promedio de 49.79x..."
}
```

**Nota:** Este endpoint es consumido por el workflow de n8n para el bot de Telegram.

#### Documentación Interactiva

FastAPI genera documentación automática:
```
http://localhost:8002/docs
```

---

## Estructura del Proyecto
```
bubbabags-mvp/
├── src/
│   ├── config.py              # Configuración y settings
│   ├── api_simple.py          # API FastAPI con endpoint /api/ask
│   ├── agent/
│   │   └── agent.py           # Agente OpenAI con function calling
│   ├── data/
│   │   ├── bigquery_client.py # Cliente BigQuery
│   │   └── views.py           # Queries y vistas
│   └── modeling/
│       ├── features.py        # Feature engineering
│       ├── train.py           # Entrenamiento del modelo
│       └── predict.py         # Predicciones
├── ui/
│   └── app.py                 # Interfaz Streamlit
├── models/
│   ├── roas_model_google_ads.json  # Modelo entrenado
│   └── training_metrics.json       # Métricas del modelo
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml     # 3 servicios (streamlit, api, n8n)
├── scripts/
│   ├── run_ui.py
│   └── train_model.py
├── .env                       # Variables de entorno
├── requirements.txt           # Dependencias Python
├── Makefile                   # Comandos útiles
└── README.md
```

---

## Modelo de Machine Learning

### Descripción

Modelo **XGBoost** entrenado para predecir ROAS (Return on Ad Spend) de campañas de Google Ads.

### Métricas de Rendimiento

| Métrica | Valor | Comparación |
|---------|-------|-------------|
| **R² Score** | 0.684 | +24.1% vs baseline histórico |
| **MAE** | 3.42 | - |
| **RMSE** | 5.18 | - |

### Features Utilizadas

- Inversión (cost)
- Impresiones
- Clicks
- CTR (Click-Through Rate)
- Conversiones
- CPC (Cost Per Click)
- Día de la semana
- Mes

### Re-entrenamiento
```bash
python scripts/train_model.py
```

El modelo se actualiza con datos históricos de BigQuery.

---

## Configuración de n8n

### ¿Por qué n8n para el Bot de Telegram?

**n8n** es una plataforma de automatización workflow-based que permite:
- Orquestar procesos complejos sin código
- Integrar múltiples servicios (Telegram + API + BigQuery)
- Programar ejecuciones automáticas
- Implementar lógica condicional (filtros anti-duplicados)
- Debugging visual de flujos

### Workflow: Bot de Telegram

El workflow está configurado para responder automáticamente a mensajes en Telegram cada 30 segundos.

#### Componentes del Workflow
```
Schedule Trigger (30 seg)
    ↓
HTTP Request (Get Telegram Updates)
    ↓
IF (Filtro de mensajes nuevos)
    ↓ (true)
HTTP Request2 (POST /api/ask)
    ↓
HTTP Request1 (Send Telegram Message)
```

#### Configuración del Schedule Trigger

- **Trigger Interval**: Seconds
- **Seconds Between Triggers**: 30

**Propósito:** Ejecutar el workflow automáticamente cada 30 segundos.

#### Configuración del Nodo IF (Anti-duplicados)

**Condición:**
- **Value 1**: `{{ $json.result[0].message.date }}`
- **Operation**: is greater than
- **Value 2**: `{{ Math.floor(Date.now() / 1000) - 30 }}`

**Propósito:** Procesar solo mensajes de los últimos 30 segundos para evitar respuestas duplicadas.

#### HTTP Request (Get Updates)

**Method**: GET  
**URL**: `https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1`

**Propósito:** Obtener el último mensaje enviado al bot.

#### HTTP Request2 (Llamada al Agente)

**Method**: POST  
**URL**: `http://api:8002/api/ask`  
**Body**:
```json
{
  "question": "{{ $('HTTP Request').item.json.result[0].message.text }}"
}
```

**Propósito:** Enviar la pregunta del usuario al agente conversacional.

#### HTTP Request1 (Respuesta a Telegram)

**Method**: POST  
**URL**: `https://api.telegram.org/bot{TOKEN}/sendMessage`  
**Body** (Using Fields Below):
- **chat_id**: `{{ $('HTTP Request').item.json.result[0].message.chat.id }}`
- **text**: `{{ $('HTTP Request2').item.json.answer }}`

**Propósito:** Enviar la respuesta del agente de vuelta al usuario en Telegram.

### Activación del Workflow

1. Abre n8n: http://localhost:5678
2. El workflow "Telegram Bot" debe estar visible
3. Activa el toggle "Active" (arriba a la derecha)
4. El bot empezará a responder automáticamente cada 30 segundos

### Monitoreo

Para ver las ejecuciones del workflow:
- Click en **"Executions"** (arriba en n8n)
- Verás historial de cada ejecución
- Puedes debuggear errores viendo los outputs de cada nodo

---

## Variables de Entorno

### Archivo `.env`
```env
# Google Cloud Platform
GCP_PROJECT_ID=tu-proyecto-id
BQ_DATASET=marketing_analytics

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Telegram (Opcional - solo para bot)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Credenciales de Google Cloud

Las credenciales deben estar en:
```
Windows: %APPDATA%\gcloud\application_default_credentials.json
Linux/Mac: ~/.config/gcloud/application_default_credentials.json
```

Generar con:
```bash
gcloud auth application-default login
```

---

## Próximas Mejoras

### Features Planificados

- [ ] **Soporte de mensajes de voz** (Whisper API)
- [ ] **Sistema robusto anti-duplicados** con tracking de message_id
- [ ] **Notificaciones proactivas** de anomalías en campañas
- [ ] **Gráficos en respuestas** de Telegram
- [ ] **Integración con Slack** usando n8n
- [ ] **Dashboard en tiempo real** con WebSockets
- [ ] **A/B Testing automatizado**
- [ ] **Recomendaciones de optimización** con RL
- [ ] **Multi-idioma** (EN/ES)
- [ ] **Autenticación** y roles de usuario

### Mejoras de Infraestructura

- [ ] **CI/CD** con GitHub Actions
- [ ] **Tests unitarios** y de integración
- [ ] **Monitoring** con Prometheus + Grafana
- [ ] **Logs centralizados** con ELK Stack
- [ ] **Rate limiting** en API
- [ ] **Cache** con Redis
- [ ] **Deployment** en GCP Cloud Run
- [ ] **Workflows n8n** adicionales para reportes automáticos

---

## Licencia

Este proyecto es privado y propiedad de Nueva EPS / Bubbabags.

---

## Contribuidores

- **Byron Torres** - Data Engineer - [GitHub](https://github.com/byrontorres)


**Última actualización**: 26 de noviembre de 2025