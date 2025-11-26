"""Endpoint para campanas."""
from fastapi import APIRouter, Query
from src.analytics.campaign_service import get_top_campaigns, get_performance_by_channel
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/campaigns")
async def list_campaigns(
    start_date: str = Query(default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")),
    end_date: str = Query(default=datetime.now().strftime("%Y-%m-%d")),
    metric: str = Query(default="roas"),
    limit: int = Query(default=10, ge=1, le=100)
):
    df = get_top_campaigns(start_date, end_date, metric, limit)
    return df.to_dict(orient="records")


@router.get("/campaigns/by-channel")
async def campaigns_by_channel(
    start_date: str = Query(default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")),
    end_date: str = Query(default=datetime.now().strftime("%Y-%m-%d"))
):
    df = get_performance_by_channel(start_date, end_date)
    return df.to_dict(orient="records")
