"""Utilidades para rangos de tiempo."""
from datetime import datetime, timedelta
from typing import Tuple


def parse_time_range(text: str) -> Tuple[str, str]:
    today = datetime.now()
    text = text.lower().strip()
    
    if "hoy" in text:
        start = end = today
    elif "ayer" in text:
        start = end = today - timedelta(days=1)
    elif "ultima semana" in text or "semana pasada" in text:
        start = today - timedelta(days=7)
        end = today
    elif "este mes" in text:
        start = today.replace(day=1)
        end = today
    elif "ultimos 30 dias" in text:
        start = today - timedelta(days=30)
        end = today
    else:
        start = today - timedelta(days=30)
        end = today
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
