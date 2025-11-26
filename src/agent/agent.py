"""
Agente Conversacional - Bubbabags Marketing MVP

Usa OpenAI directamente con function calling.
"""
import json
from openai import OpenAI

from src.config import settings
from src.data.views import (
    get_channel_summary,
    get_campaign_performance_daily,
    get_campaign_performance_monthly
)
from src.modeling.predict import (
    get_top_campaigns_by_predicted_roas,
    get_prediction_summary
)


# =============================================================================
# CLIENTE OPENAI
# =============================================================================
client = OpenAI(api_key=settings.openai_api_key)


# =============================================================================
# FUNCIONES DE DATOS
# =============================================================================
def get_channel_comparison() -> str:
    """Obtiene resumen comparativo de Google Ads vs Meta Ads."""
    try:
        df = get_channel_summary()
        result = []
        for _, row in df.iterrows():
            result.append({
                "canal": row["channel"],
                "campanas": int(row["total_campaigns"]),
                "impresiones": int(row["total_impressions"]),
                "clicks": int(row["total_clicks"]),
                "costo_total": round(row["total_cost"], 2),
                "revenue_total": round(row["total_revenue"], 2),
                "ctr_promedio": round(row["avg_ctr"] * 100, 2),
                "roas_promedio": round(row["avg_roas"], 2)
            })
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_top_campaigns() -> str:
    """Obtiene las campañas con mejor ROAS."""
    try:
        df = get_top_campaigns_by_predicted_roas(top_n=10)

        if df.empty:
            return json.dumps({"mensaje": "No hay datos disponibles"})

        result = []
        for _, row in df.iterrows():
            result.append({
                "campana": row["campaign_name"][:50],
                "canal": row["channel"],
                "roas": round(row["predicted_roas"], 2),
                "costo": round(row["cost"], 2),
                "revenue": round(row["revenue"], 2)
            })
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_monthly_performance() -> str:
    """Obtiene rendimiento mensual de campañas."""
    try:
        df = get_campaign_performance_monthly()
        
        if df.empty:
            return json.dumps({"mensaje": "No hay datos disponibles"})

        df = df.head(15)

        result = []
        for _, row in df.iterrows():
            result.append({
                "mes": row["month"],
                "campana": row["campaign_name"][:40],
                "canal": row["channel"],
                "impresiones": int(row["impressions"]),
                "clicks": int(row["clicks"]),
                "costo": round(row["cost"], 2),
                "revenue": round(row["revenue"], 2),
                "ctr": round(row["ctr"] * 100, 2) if row["ctr"] else 0,
                "roas": round(row["roas"], 2) if row["roas"] else 0
            })
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_predictions_info() -> str:
    """Obtiene información del sistema de predicción."""
    try:
        summary = get_prediction_summary()
        top_df = get_top_campaigns_by_predicted_roas(top_n=5)

        result = {
            "sistema": summary,
            "top_campanas_predichas": []
        }

        for _, row in top_df.iterrows():
            result["top_campanas_predichas"].append({
                "campana": row["campaign_name"][:40],
                "canal": row["channel"],
                "roas_esperado": round(row["predicted_roas"], 2)
            })

        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_kpi_evolution() -> str:
    """Obtiene evolución de KPIs por día y canal."""
    try:
        df = get_campaign_performance_daily()

        if df.empty:
            return json.dumps({"mensaje": "No hay datos disponibles"})

        daily = df.groupby(["date", "channel"]).agg({
            "impressions": "sum",
            "clicks": "sum",
            "cost": "sum",
            "revenue": "sum"
        }).reset_index()

        daily["ctr"] = (daily["clicks"] / daily["impressions"] * 100).round(2)
        daily["roas"] = (daily["revenue"] / daily["cost"]).round(2)
        daily = daily.sort_values("date", ascending=False).head(14)

        result = []
        for _, row in daily.iterrows():
            result.append({
                "fecha": str(row["date"])[:10],
                "canal": row["channel"],
                "ctr": float(row["ctr"]) if row["ctr"] else 0,
                "roas": float(row["roas"]) if row["roas"] else 0,
                "costo": round(row["cost"], 2)
            })

        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# DEFINICION DE TOOLS PARA OPENAI
# =============================================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_channel_comparison",
            "description": "Compara el rendimiento de Google Ads vs Meta Ads. Incluye ROAS, CTR, costos y revenue por canal.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_campaigns",
            "description": "Lista las campañas con mejor ROAS histórico. Útil para saber qué campañas tienen mejor retorno.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_monthly_performance",
            "description": "Obtiene métricas de rendimiento mensual por campaña: impresiones, clicks, CTR, ROAS, costos.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_predictions_info",
            "description": "Obtiene predicciones de ROAS usando ML. Google Ads usa XGBoost, Meta Ads usa baseline histórico.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_kpi_evolution",
            "description": "Muestra la evolución de KPIs (CTR, ROAS, costos) por día y canal en las últimas 2 semanas.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

AVAILABLE_FUNCTIONS = {
    "get_channel_comparison": get_channel_comparison,
    "get_top_campaigns": get_top_campaigns,
    "get_monthly_performance": get_monthly_performance,
    "get_predictions_info": get_predictions_info,
    "get_kpi_evolution": get_kpi_evolution
}


# =============================================================================
# AGENTE
# =============================================================================
SYSTEM_PROMPT = """Eres un asistente experto en marketing digital para Bubbabags.

Tu rol es responder preguntas sobre campañas de Google Ads y Meta Ads usando datos reales.

Las herramientas devuelven datos en JSON. Debes:
- Interpretar los números
- Responder en español, de forma clara y concisa
- NO mostrar JSON crudo, solo insights en lenguaje natural
- Incluir números específicos cuando sea relevante

Para predicciones, explica que:
- Google Ads usa modelo XGBoost (R² 0.684, +24% vs baseline)
- Meta Ads usa baseline histórico (R² 0.567)
"""


def ask(question: str, verbose: bool = False) -> str:
    """Hace una pregunta al agente y retorna la respuesta."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    # Primera llamada: el modelo decide si usar tools
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Si el modelo quiere usar tools
    if assistant_message.tool_calls:
        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name

            if verbose:
                print(f"  [Tool: {function_name}]")

            # Ejecutar la función
            if function_name in AVAILABLE_FUNCTIONS:
                function_response = AVAILABLE_FUNCTIONS[function_name]()
            else:
                function_response = json.dumps({"error": f"Función {function_name} no encontrada"})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_response
            })

        # Segunda llamada: el modelo genera la respuesta final
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        return final_response.choices[0].message.content

    else:
        return assistant_message.content


def run_agent(question: str) -> str:
    """
    Función wrapper para compatibilidad con la API.
    Ejecuta el agente con una pregunta y retorna la respuesta.
    
    Args:
        question: Pregunta en lenguaje natural sobre campañas de marketing
        
    Returns:
        Respuesta del agente en formato texto
    """
    return ask(question, verbose=False)


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("AGENTE DE MARKETING - BUBBABAGS")
    print("=" * 60)

    test_questions = [
        "¿Cuál canal tiene mejor ROAS, Google Ads o Meta Ads?",
        "¿Cuál fue la campaña con mayor ROAS?",
        "¿Qué campaña debería tener mejor rendimiento en el futuro?"
    ]

    for q in test_questions:
        print(f"\n>>> PREGUNTA: {q}")
        print("-" * 40)
        response = ask(q, verbose=True)
        print(f"\nRESPUESTA: {response}")
        print("=" * 60)