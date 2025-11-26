"""Almacenamiento y carga de modelos."""
import os
import joblib
from datetime import datetime
from src.config import settings


def get_model_path() -> str:
    return settings.model_path


def save_model(model, feature_columns: list, metadata: dict = None) -> str:
    model_path = get_model_path()
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    model_data = {
        "model": model,
        "feature_columns": feature_columns,
        "version": settings.model_version,
        "trained_at": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    joblib.dump(model_data, model_path)
    print(f"\nModelo guardado en: {model_path}")
    return model_path


def load_model() -> dict:
    model_path = get_model_path()
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modelo no encontrado en {model_path}. Ejecuta 'make train' primero.")
    return joblib.load(model_path)


def model_exists() -> bool:
    return os.path.exists(get_model_path())
