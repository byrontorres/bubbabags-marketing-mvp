"""Construccion de features para el modelo de prediccion de ROAS."""
import pandas as pd
import numpy as np
from src.data.views import get_roas_training_dataset


def build_features_dataframe(lookback_days: int = 90) -> pd.DataFrame:
    """
    Construye el dataframe de features para entrenar el modelo.
    Incluye limpieza de datos, tratamiento de outliers y normalizacion.
    """
    df = get_roas_training_dataset(lookback_days)
    
    if df.empty:
        return df
    
    # Asegurar que date es datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # =========================================================================
    # LIMPIEZA DE DATOS
    # =========================================================================
    
    # 1. Eliminar registros con cost = 0 (ya viene filtrado pero por seguridad)
    df = df[df["cost"] > 0].copy()
    
    # 2. Filtrar campañas con muy pocos registros (min 10 por campaña)
    campaign_counts = df.groupby("campaign_id").size()
    valid_campaigns = campaign_counts[campaign_counts >= 10].index
    df = df[df["campaign_id"].isin(valid_campaigns)].copy()
    
    # =========================================================================
    # TRATAMIENTO DE OUTLIERS
    # =========================================================================
    
    # 3. Winsorización: limitar ROAS al percentil 95 por canal
    for channel in df["channel"].unique():
        mask = df["channel"] == channel
        p95 = df.loc[mask, "roas"].quantile(0.95)
        df.loc[mask, "roas"] = df.loc[mask, "roas"].clip(upper=p95)
    
    # 4. Clip final de seguridad (max 100)
    df["roas"] = df["roas"].clip(upper=100)
    
    # 5. Winsorización de features numéricas extremas
    numeric_cols = ["impressions", "clicks", "cost", "ctr", "cpc"]
    for col in numeric_cols:
        if col in df.columns:
            # Convertir a float para evitar problemas de tipo
            df[col] = df[col].astype(float)
            p99 = df[col].quantile(0.99)
            df[col] = df[col].clip(upper=p99)
    
    # =========================================================================
    # FEATURE ENGINEERING
    # =========================================================================
    df = add_derived_features(df)
    
    # =========================================================================
    # LIMPIEZA FINAL
    # =========================================================================
    
    # Limpiar valores nulos e infinitos
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=get_feature_columns() + [get_target_column()])
    
    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega features derivadas al dataframe."""
    df = df.copy()
    
    # Log de cost para normalizar (reduce efecto de outliers)
    if "cost" in df.columns:
        df["log_cost"] = np.log1p(df["cost"])
    
    # Log de impressions
    if "impressions" in df.columns:
        df["log_impressions"] = np.log1p(df["impressions"])
    
    # Ratio clicks/impressions adicional
    if "clicks" in df.columns and "impressions" in df.columns:
        df["click_impression_ratio"] = df["clicks"] / (df["impressions"] + 1)
    
    # Feature de canal como variable numérica
    if "channel" in df.columns:
        df["is_google_ads"] = (df["channel"] == "google_ads").astype(int)
    
    # Feature de eficiencia de costo
    if "cost" in df.columns and "clicks" in df.columns:
        df["cost_per_click_ratio"] = df["cost"] / (df["clicks"] + 1)
    
    # Feature de engagement
    if "clicks" in df.columns and "impressions" in df.columns:
        df["engagement_score"] = (df["clicks"] * 100) / (df["impressions"] + 1)
    
    return df


def get_feature_columns() -> list[str]:
    """Retorna las columnas que se usan como features."""
    return [
        "impressions",
        "clicks", 
        "cost",
        "ctr",
        "cpc",
        "day_of_week",
        "is_weekend",
        "month",
        "log_cost",
        "log_impressions",
        "click_impression_ratio",
        "is_google_ads"
    ]


def get_target_column() -> str:
    """Retorna la columna target (lo que predecimos)."""
    return "roas"


def temporal_train_valid_test_split(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    valid_ratio: float = 0.15
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split temporal: entrena con pasado, valida con presente, testea con futuro.
    """
    df = df.sort_values("date").reset_index(drop=True)
    
    dates = df["date"].sort_values().unique()
    n = len(dates)
    
    if n < 3:
        raise ValueError(f"Se necesitan al menos 3 fechas distintas, hay solo {n}.")
    
    train_end_idx = int(n * train_ratio)
    valid_end_idx = int(n * (train_ratio + valid_ratio))
    
    train_end_date = dates[train_end_idx]
    valid_end_date = dates[valid_end_idx]
    
    train_df = df[df["date"] <= train_end_date].copy()
    valid_df = df[(df["date"] > train_end_date) & (df["date"] <= valid_end_date)].copy()
    test_df = df[df["date"] > valid_end_date].copy()
    
    return train_df, valid_df, test_df