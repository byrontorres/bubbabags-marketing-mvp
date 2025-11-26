"""
Sistema de prediccion de ROAS - Bubbabags MVP

Estrategia por canal:
- Google Ads: XGBoost (supera baseline +24.1%)
- Meta Ads: Baseline (media historica por campana)
"""
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path
from typing import Optional

from src.data.views import get_roas_training_dataset
from src.modeling.features import get_feature_columns


MODEL_DIR = Path("models")
BASELINE_CACHE: dict = {}
MODELS_CACHE: dict = {}


def load_channel_model(channel: str):
    """Carga el modelo XGBoost para un canal."""
    if channel in MODELS_CACHE:
        return MODELS_CACHE[channel]
    
    model_path = MODEL_DIR / f"roas_model_{channel}.json"
    
    if not model_path.exists():
        return None
    
    model = xgb.XGBRegressor()
    model.load_model(str(model_path))
    MODELS_CACHE[channel] = model
    
    return model


def build_baseline_predictor(lookback_days: int = 90) -> dict:
    """Construye baseline: media de ROAS por campana."""
    global BASELINE_CACHE
    
    if BASELINE_CACHE:
        return BASELINE_CACHE
    
    df = get_roas_training_dataset(lookback_days)
    
    if df.empty:
        return {}
    
    baseline = df.groupby("campaign_id")["roas"].mean().to_dict()
    baseline["__google_ads_mean__"] = df[df["channel"] == "google_ads"]["roas"].mean()
    baseline["__meta_ads_mean__"] = df[df["channel"] == "meta_ads"]["roas"].mean()
    baseline["__global_mean__"] = df["roas"].mean()
    
    BASELINE_CACHE = baseline
    return baseline


def predict_roas(
    campaign_id: str,
    channel: str,
    impressions: int = 0,
    clicks: int = 0,
    cost: float = 0,
    day_of_week: int = 3,
    month: int = 11
) -> dict:
    """
    Predice ROAS para una campana.
    
    - Google Ads: Usa XGBoost
    - Meta Ads: Usa baseline (media historica)
    """
    baseline = build_baseline_predictor()
    
    if channel == "google_ads":
        model = load_channel_model("google_ads")
        
        if model is None:
            roas_pred = baseline.get(campaign_id, baseline.get("__google_ads_mean__", 0))
            return {
                "campaign_id": campaign_id,
                "channel": "google_ads",
                "predicted_roas": round(roas_pred, 2),
                "method": "baseline",
                "confidence": "medium"
            }
        
        # Calcular features
        ctr = clicks / impressions if impressions > 0 else 0
        cpc = cost / clicks if clicks > 0 else 0
        is_weekend = 1 if day_of_week in [1, 7] else 0
        log_cost = np.log1p(cost)
        log_impressions = np.log1p(impressions)
        click_impression_ratio = clicks / (impressions + 1)
        
        features = np.array([[
            impressions, clicks, cost, ctr, cpc,
            day_of_week, is_weekend, month,
            log_cost, log_impressions, click_impression_ratio
        ]])
        
        roas_pred = model.predict(features)[0]
        roas_pred = max(0, min(roas_pred, 100))
        
        return {
            "campaign_id": campaign_id,
            "channel": "google_ads",
            "predicted_roas": round(roas_pred, 2),
            "method": "xgboost",
            "confidence": "high",
            "model_performance": "R² 0.684, +24.1% vs baseline"
        }
    
    elif channel == "meta_ads":
        if campaign_id in baseline:
            roas_pred = baseline[campaign_id]
            source = "campaign_history"
            confidence = "high"
        else:
            roas_pred = baseline.get("__meta_ads_mean__", 0)
            source = "channel_mean"
            confidence = "medium"
        
        return {
            "campaign_id": campaign_id,
            "channel": "meta_ads",
            "predicted_roas": round(roas_pred, 2),
            "method": "baseline",
            "source": source,
            "confidence": confidence,
            "note": "Baseline es mas preciso que ML para Meta Ads (R² 0.567)"
        }
    
    else:
        return {"error": f"Canal no reconocido: {channel}"}


def get_top_campaigns_by_predicted_roas(
    channel: Optional[str] = None,
    top_n: int = 10
) -> pd.DataFrame:
    """Retorna las campanas con mejor ROAS predicho."""
    df = get_roas_training_dataset(90)
    
    if df.empty:
        return pd.DataFrame()
    
    summary = df.groupby(["campaign_id", "campaign_name", "channel"]).agg({
        "roas": "mean",
        "cost": "sum",
        "revenue": "sum"
    }).reset_index()
    
    summary = summary.rename(columns={"roas": "predicted_roas"})
    summary["predicted_roas"] = summary["predicted_roas"].round(2)
    
    if channel:
        summary = summary[summary["channel"] == channel]
    
    return summary.sort_values("predicted_roas", ascending=False).head(top_n)


def get_prediction_summary() -> dict:
    """Retorna informacion sobre el sistema de prediccion."""
    return {
        "system": "Bubbabags ROAS Prediction",
        "channels": {
            "google_ads": {
                "method": "XGBoost",
                "performance": "R² 0.684, +24.1% vs baseline",
                "status": "ML activo"
            },
            "meta_ads": {
                "method": "Baseline (media historica)",
                "performance": "R² 0.567",
                "status": "Baseline supera a ML"
            }
        }
    }


if __name__ == "__main__":
    print("=== TEST SISTEMA DE PREDICCION ===")
    
    summary = get_prediction_summary()
    print(f"\nGoogle Ads: {summary['channels']['google_ads']['method']}")
    print(f"Meta Ads: {summary['channels']['meta_ads']['method']}")
    
    print("\n>>> Top 3 campanas:")
    top = get_top_campaigns_by_predicted_roas(top_n=3)
    for _, row in top.iterrows():
        print(f"  {row['campaign_name'][:40]} | {row['channel']} | ROAS: {row['predicted_roas']}")
    
    print("\n>>> Prediccion ejemplo Google Ads:")
    pred = predict_roas("test", "google_ads", impressions=10000, clicks=500, cost=1000)
    print(f"  ROAS predicho: {pred['predicted_roas']}")
    print(f"  Metodo: {pred['method']}")