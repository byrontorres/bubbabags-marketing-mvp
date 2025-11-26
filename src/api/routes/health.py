"""Endpoint de health check."""
from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.data.bigquery_client import test_connection
from src.modeling.model_store import model_exists
from src.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        bigquery=test_connection(),
        model_loaded=model_exists(),
        version=settings.model_version
    )
