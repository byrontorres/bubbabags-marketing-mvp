"""
API Simple para integración con n8n
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.data.views import get_channel_summary
from src.modeling.predict import get_top_campaigns_by_predicted_roas, get_prediction_summary

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bubbabags Marketing API",
    description="API para integración con n8n",
    version="1.0.0"
)

# Permitir CORS para n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelo para el request del agente
class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "ok", "message": "Bubbabags Marketing API"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.get("/api/channel-summary")
def channel_summary():
    """Resumen de rendimiento por canal."""
    try:
        df = get_channel_summary()
        return {
            "status": "success",
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/top-campaigns")
def top_campaigns(limit: int = 5):
    """Top campañas por ROAS."""
    try:
        df = get_top_campaigns_by_predicted_roas(top_n=limit)
        return {
            "status": "success",
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/prediction-summary")
def prediction_summary():
    """Resumen del sistema de predicción."""
    try:
        summary = get_prediction_summary()
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    """
    Endpoint para preguntas en lenguaje natural usando el agente OpenAI.
    
    Body esperado:
    {
        "question": "¿Cuál canal tiene mejor ROAS?"
    }
    """
    try:
        question = request.question
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        logger.info(f"Pregunta recibida: {question}")
        
        # Importar el agente
        from src.agent.agent import run_agent
        
        # Ejecutar el agente con la pregunta
        response = run_agent(question)
        
        logger.info(f"Respuesta generada: {response[:100]}...")
        
        return {
            "status": "success",
            "question": question,
            "answer": response
        }
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)