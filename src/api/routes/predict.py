"""Endpoint para prediccion."""
from fastapi import APIRouter, HTTPException
from src.api.schemas import PredictRequest, PredictResponse
from src.modeling.predict import predict_campaign_roas

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict_roas(request: PredictRequest):
    try:
        result = predict_campaign_roas(request.campaign_id, request.proposed_spend)
        return PredictResponse(**result)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Modelo no entrenado. Ejecuta 'make train'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
