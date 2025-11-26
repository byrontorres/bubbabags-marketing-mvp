"""Construccion de respuestas."""
import pandas as pd
from src.agent.llm_client import get_llm_client


def build_response(question: str, data: pd.DataFrame, intent: str = None) -> str:
    if data.empty:
        return "No encontre datos para tu consulta."
    
    llm = get_llm_client()
    data_summary = data.head(10).to_string()
    
    system_prompt = """Eres un analista de marketing experto. 
Genera una respuesta clara basada en los datos.
Responde en espanol. Destaca insights importantes.
No menciones que eres una IA."""
    
    prompt = f"""Pregunta: {question}

Datos:
{data_summary}

Genera una respuesta util."""
    
    return llm.complete(prompt, system_prompt)


def format_table_response(df: pd.DataFrame, max_rows: int = 10) -> str:
    if df.empty:
        return "_Sin datos_"
    return df.head(max_rows).to_markdown(index=False)
