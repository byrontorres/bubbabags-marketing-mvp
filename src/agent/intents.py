"""Clasificacion de intenciones."""
from enum import Enum
from src.agent.llm_client import get_llm_client


class Intent(Enum):
    DESCRIPTIVE = "descriptive"
    RANKING = "ranking"
    COMPARATIVE = "comparative"
    EVOLUTION = "evolution"
    PREDICTION = "prediction"
    OPTIMIZATION = "optimization"
    UNKNOWN = "unknown"


def classify_intent(question: str) -> Intent:
    llm = get_llm_client()
    
    system_prompt = """Eres un clasificador de intenciones para marketing.
    
Clasifica la pregunta en UNA categoria:
- descriptive: Metricas actuales o pasadas
- ranking: Top/mejores/peores campanas
- comparative: Comparaciones entre canales o campanas
- evolution: Tendencias o evolucion en el tiempo
- prediction: Predicciones futuras
- optimization: Recomendaciones de optimizacion
- unknown: No relacionada con marketing

Responde SOLO el nombre de la categoria."""
    
    response = llm.complete(question, system_prompt)
    
    intent_map = {
        "descriptive": Intent.DESCRIPTIVE,
        "ranking": Intent.RANKING,
        "comparative": Intent.COMPARATIVE,
        "evolution": Intent.EVOLUTION,
        "prediction": Intent.PREDICTION,
        "optimization": Intent.OPTIMIZATION
    }
    
    return intent_map.get(response.strip().lower(), Intent.UNKNOWN)
