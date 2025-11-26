"""Schemas Pydantic."""
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., description="Pregunta en lenguaje natural")


class AskResponse(BaseModel):
    response: str
    table: str | None = None
    data: list[dict] = []
    sql: str | None = None
    intent: str
    success: bool


class PredictRequest(BaseModel):
    campaign_id: str
    proposed_spend: float = Field(..., gt=0)


class PredictResponse(BaseModel):
    campaign_id: str
    proposed_spend: float
    predicted_roas: float
    estimated_revenue: float
    confidence_range: dict


class HealthResponse(BaseModel):
    status: str
    bigquery: bool
    model_loaded: bool
    version: str
