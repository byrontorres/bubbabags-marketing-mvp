"""
Script profesional de entrenamiento - MODELOS POR CANAL

Entrena un modelo separado para Google Ads y otro para Meta Ads.
Incluye fallback a modelo simple (Ridge) si XGBoost no funciona.
"""
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from datetime import datetime
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from joblib import dump

from src.modeling.features import (
    build_features_dataframe,
    get_feature_columns,
    get_target_column,
    temporal_train_valid_test_split
)


# =============================================================================
# CONFIGURACION
# =============================================================================
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

HYPERPARAMS_XGBOOST = {
    "max_depth": 3,
    "learning_rate": 0.03,
    "n_estimators": 500,
    "subsample": 0.7,
    "colsample_bytree": 0.7,
    "reg_lambda": 2.0,
    "reg_alpha": 1.0,
    "min_child_weight": 5,
    "gamma": 0.5,
    "random_state": 42,
}

HYPERPARAMS_RIDGE = {
    "alpha": 10.0,
    "random_state": 42,
}


# =============================================================================
# FUNCIONES DE EVALUACION
# =============================================================================
def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, name: str) -> dict:
    """Calcula metricas de evaluacion."""
    y_pred = np.clip(y_pred, 0, None)
    
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    print(f"  {name:15} -> RMSE: {rmse:8.2f} | MAE: {mae:8.2f} | R²: {r2:6.3f}")
    
    return {"rmse": float(rmse), "mae": float(mae), "r2": float(r2)}


def calculate_baseline_predictions(train_df: pd.DataFrame, eval_df: pd.DataFrame) -> np.ndarray:
    """Baseline: ROAS promedio por campaña."""
    target = get_target_column()
    baseline_by_campaign = train_df.groupby("campaign_id")[target].mean()
    global_mean = train_df[target].mean()
    
    baseline_pred = eval_df["campaign_id"].map(baseline_by_campaign).fillna(global_mean)
    return baseline_pred.values


# =============================================================================
# ENTRENAMIENTO XGBOOST
# =============================================================================
def train_xgboost(X_train, y_train, X_valid, y_valid, hyperparams):
    """Entrena modelo XGBoost."""
    model = xgb.XGBRegressor(
        max_depth=hyperparams["max_depth"],
        learning_rate=hyperparams["learning_rate"],
        n_estimators=hyperparams["n_estimators"],
        subsample=hyperparams["subsample"],
        colsample_bytree=hyperparams["colsample_bytree"],
        reg_lambda=hyperparams["reg_lambda"],
        reg_alpha=hyperparams["reg_alpha"],
        min_child_weight=hyperparams["min_child_weight"],
        gamma=hyperparams["gamma"],
        random_state=hyperparams["random_state"],
        n_jobs=-1
    )
    
    model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)], verbose=False)
    
    return model, "xgboost"


# =============================================================================
# ENTRENAMIENTO RIDGE (FALLBACK)
# =============================================================================
def train_ridge(X_train, y_train, hyperparams):
    """Entrena modelo Ridge con transformacion log del target."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = Ridge(alpha=hyperparams["alpha"], random_state=hyperparams["random_state"])
    model.fit(X_train_scaled, y_train)
    
    # Guardar scaler junto con el modelo
    model.scaler = scaler
    
    return model, "ridge"


# =============================================================================
# ENTRENAMIENTO POR CANAL
# =============================================================================
def train_channel_model(df: pd.DataFrame, channel: str) -> dict:
    """
    Entrena un modelo para un canal especifico.
    Usa XGBoost primero, si no supera baseline usa Ridge.
    """
    print(f"\n{'='*60}")
    print(f"ENTRENANDO MODELO: {channel.upper()}")
    print(f"{'='*60}")
    
    # Filtrar por canal
    df_channel = df[df["channel"] == channel].copy()
    
    if len(df_channel) < 30:
        print(f"  ⚠️  Datos insuficientes: {len(df_channel)} registros")
        return {"status": "skipped", "reason": "insufficient_data"}
    
    print(f"  Total registros: {len(df_channel)}")
    
    # Split temporal
    train_df, valid_df, test_df = temporal_train_valid_test_split(df_channel)
    
    print(f"  Train: {len(train_df)} ({train_df['date'].min().date()} - {train_df['date'].max().date()})")
    print(f"  Valid: {len(valid_df)} ({valid_df['date'].min().date()} - {valid_df['date'].max().date()})")
    print(f"  Test:  {len(test_df)} ({test_df['date'].min().date()} - {test_df['date'].max().date()})")
    
    # Features
    features = [f for f in get_feature_columns() if f != "is_google_ads"]
    target = get_target_column()
    
    X_train = train_df[features].values
    y_train = train_df[target].values
    X_valid = valid_df[features].values
    y_valid = valid_df[target].values
    X_test = test_df[features].values
    y_test = test_df[target].values
    
    # Transformacion log del target para estabilizar
    y_train_log = np.log1p(y_train)
    y_valid_log = np.log1p(y_valid)
    y_test_log = np.log1p(y_test)
    
    # Baseline
    print(f"\n  >>> Baseline (media por campaña):")
    y_test_baseline = calculate_baseline_predictions(train_df, test_df)
    baseline_test = evaluate_predictions(y_test, y_test_baseline, "BASELINE-TEST")
    
    # =========================================================================
    # INTENTO 1: XGBoost
    # =========================================================================
    print(f"\n  >>> Entrenando XGBoost...")
    xgb_model, _ = train_xgboost(X_train, y_train, X_valid, y_valid, HYPERPARAMS_XGBOOST)
    
    y_test_pred_xgb = xgb_model.predict(X_test)
    xgb_test = evaluate_predictions(y_test, y_test_pred_xgb, "XGBOOST-TEST")
    
    xgb_improvement = ((baseline_test["rmse"] - xgb_test["rmse"]) / baseline_test["rmse"]) * 100
    print(f"  XGBoost vs Baseline: {xgb_improvement:+.1f}%")
    
    # =========================================================================
    # INTENTO 2: Ridge con log-transform (si XGBoost falla)
    # =========================================================================
    print(f"\n  >>> Entrenando Ridge (log-transform)...")
    ridge_model, _ = train_ridge(X_train, y_train_log, HYPERPARAMS_RIDGE)
    
    X_test_scaled = ridge_model.scaler.transform(X_test)
    y_test_pred_ridge_log = ridge_model.predict(X_test_scaled)
    y_test_pred_ridge = np.expm1(y_test_pred_ridge_log)  # Revertir log
    y_test_pred_ridge = np.clip(y_test_pred_ridge, 0, 200)  # Clip extremos
    
    ridge_test = evaluate_predictions(y_test, y_test_pred_ridge, "RIDGE-TEST")
    
    ridge_improvement = ((baseline_test["rmse"] - ridge_test["rmse"]) / baseline_test["rmse"]) * 100
    print(f"  Ridge vs Baseline: {ridge_improvement:+.1f}%")
    
    # =========================================================================
    # SELECCIONAR MEJOR MODELO
    # =========================================================================
    print(f"\n  >>> Seleccionando mejor modelo...")
    
    models_performance = [
        ("xgboost", xgb_model, xgb_test, xgb_improvement),
        ("ridge", ridge_model, ridge_test, ridge_improvement),
        ("baseline", None, baseline_test, 0)
    ]
    
    # Ordenar por RMSE (menor es mejor)
    models_performance.sort(key=lambda x: x[2]["rmse"])
    
    best_name, best_model, best_metrics, best_improvement = models_performance[0]
    
    print(f"\n  🏆 MEJOR MODELO: {best_name.upper()}")
    print(f"     RMSE: {best_metrics['rmse']:.2f}")
    print(f"     R²: {best_metrics['r2']:.3f}")
    
    # Guardar el mejor modelo
    if best_name == "xgboost":
        model_path = MODEL_DIR / f"roas_model_{channel}.json"
        best_model.save_model(str(model_path))
        model_type = "xgboost"
    elif best_name == "ridge":
        model_path = MODEL_DIR / f"roas_model_{channel}.joblib"
        dump(best_model, model_path)
        model_type = "ridge"
    else:
        model_path = None
        model_type = "baseline"
    
    if model_path:
        print(f"  Modelo guardado: {model_path}")
    
    # Feature importance (solo para XGBoost)
    feature_importance = []
    if best_name == "xgboost":
        importance = pd.DataFrame({
            "feature": features,
            "importance": best_model.feature_importances_
        }).sort_values("importance", ascending=False)
        feature_importance = importance.head(10).to_dict(orient="records")
        
        print(f"\n  >>> Feature Importance (Top 5):")
        for _, row in importance.head(5).iterrows():
            print(f"      {row['feature']:25} {row['importance']:.4f}")
    
    return {
        "status": "trained",
        "channel": channel,
        "model_type": model_type,
        "model_path": str(model_path) if model_path else None,
        "features": features,
        "data_splits": {
            "train": len(train_df),
            "valid": len(valid_df),
            "test": len(test_df)
        },
        "baseline_metrics": {"test": baseline_test},
        "xgboost_metrics": {"test": xgb_test, "improvement": float(xgb_improvement)},
        "ridge_metrics": {"test": ridge_test, "improvement": float(ridge_improvement)},
        "best_model": {
            "name": best_name,
            "metrics": best_metrics,
            "improvement_vs_baseline": float(best_improvement)
        },
        "feature_importance": feature_importance
    }


# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================
def train_all_models(lookback_days: int = 90) -> dict:
    """Entrena modelos separados para cada canal."""
    print("=" * 60)
    print("ENTRENAMIENTO MODELOS ROAS - POR CANAL")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Lookback: {lookback_days} dias")
    
    # Cargar datos
    print("\n>>> Cargando datos...")
    df = build_features_dataframe(lookback_days)
    
    if df.empty:
        raise ValueError("No hay datos disponibles")
    
    print(f"Total registros: {len(df)}")
    print(f"Registros Google Ads: {len(df[df.channel == 'google_ads'])}")
    print(f"Registros Meta Ads: {len(df[df.channel == 'meta_ads'])}")
    
    # Entrenar modelo por canal
    results = {
        "timestamp": datetime.now().isoformat(),
        "lookback_days": lookback_days,
        "models": {}
    }
    
    for channel in ["google_ads", "meta_ads"]:
        result = train_channel_model(df, channel)
        results["models"][channel] = result
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    
    for channel, result in results["models"].items():
        if result["status"] == "trained":
            best = result["best_model"]
            print(f"{channel:15} | Mejor: {best['name']:8} | R² test: {best['metrics']['r2']:.3f} | vs baseline: {best['improvement_vs_baseline']:+.1f}%")
        else:
            print(f"{channel:15} | SKIPPED: {result.get('reason', 'unknown')}")
    
    # Guardar metricas
    metrics_path = MODEL_DIR / "training_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nMetricas guardadas: {metrics_path}")
    
    print("\n" + "=" * 60)
    print("ENTRENAMIENTO COMPLETADO")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    train_all_models(lookback_days=90)