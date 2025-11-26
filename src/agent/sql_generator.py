"""Generacion de SQL."""
from src.agent.intents import Intent
from src.agent.llm_client import get_llm_client
from src.config import settings


SQL_TEMPLATES = {
    Intent.RANKING: """
SELECT 
    campaign_name,
    channel,
    SUM(impressions) as impressions,
    SUM(clicks) as clicks,
    SUM(cost) as cost,
    SUM(revenue) as revenue,
    SAFE_DIVIDE(SUM(revenue), SUM(cost)) as roas
FROM `{project}.{dataset}.v_campaign_performance_daily`
WHERE date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1, 2
ORDER BY {metric} DESC
LIMIT {limit}
""",
    Intent.COMPARATIVE: """
SELECT 
    channel,
    SUM(impressions) as impressions,
    SUM(clicks) as clicks,
    SUM(cost) as cost,
    SUM(revenue) as revenue,
    SAFE_DIVIDE(SUM(revenue), SUM(cost)) as roas
FROM `{project}.{dataset}.v_campaign_performance_daily`
WHERE date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1
ORDER BY cost DESC
""",
    Intent.EVOLUTION: """
SELECT 
    date,
    SUM(impressions) as impressions,
    SUM(clicks) as clicks,
    SUM(cost) as cost,
    SUM(revenue) as revenue,
    SAFE_DIVIDE(SUM(revenue), SUM(cost)) as roas
FROM `{project}.{dataset}.v_campaign_performance_daily`
WHERE date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1
ORDER BY date
"""
}


def generate_sql(intent: Intent, parameters: dict) -> str:
    params = {
        "project": settings.gcp_project_id,
        "dataset": settings.bq_dataset,
        "start_date": parameters.get("start_date", "2024-01-01"),
        "end_date": parameters.get("end_date", "2024-12-31"),
        "metric": parameters.get("metric", "roas"),
        "limit": parameters.get("limit", 10)
    }
    
    template = SQL_TEMPLATES.get(intent, SQL_TEMPLATES[Intent.RANKING])
    return template.format(**params).strip()


def extract_parameters(question: str) -> dict:
    llm = get_llm_client()
    
    system_prompt = """Extrae parametros de la pregunta de marketing.

Responde en JSON con estos campos (usa null si no aplica):
- start_date: fecha inicio (YYYY-MM-DD)
- end_date: fecha fin (YYYY-MM-DD)
- channel: canal (google_ads, meta_ads, ga4)
- campaign_name: nombre de campana
- metric: metrica principal (roas, ctr, cpc, cpa, revenue, cost)
- limit: numero de resultados
- budget: presupuesto propuesto si se menciona (numero)

Si menciona "este mes", usa el mes actual.
Si menciona "ultima semana", usa los ultimos 7 dias.
Responde SOLO el JSON."""
    
    response = llm.complete(question, system_prompt)
    
    try:
        import json
        return json.loads(response)
    except:
        return {}
