"""Calculo de metricas de marketing."""
import pandas as pd


def calc_ctr(clicks: float, impressions: float) -> float | None:
    if impressions is None or impressions == 0:
        return None
    return round(clicks / impressions, 6)


def calc_cpc(cost: float, clicks: float) -> float | None:
    if clicks is None or clicks == 0:
        return None
    return round(cost / clicks, 4)


def calc_cpa(cost: float, conversions: float) -> float | None:
    if conversions is None or conversions == 0:
        return None
    return round(cost / conversions, 4)


def calc_roas(revenue: float, cost: float) -> float | None:
    if cost is None or cost == 0:
        return None
    return round(revenue / cost, 4)


def calc_cpm(cost: float, impressions: float) -> float | None:
    if impressions is None or impressions == 0:
        return None
    return round((cost / impressions) * 1000, 4)


def add_metrics_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    if "impressions" in df.columns and "clicks" in df.columns:
        df["ctr"] = df.apply(
            lambda row: calc_ctr(row.get("clicks", 0), row.get("impressions", 0)), 
            axis=1
        )
    
    if "cost" in df.columns and "clicks" in df.columns:
        df["cpc"] = df.apply(
            lambda row: calc_cpc(row.get("cost", 0), row.get("clicks", 0)), 
            axis=1
        )
    
    if "cost" in df.columns and "conversions" in df.columns:
        df["cpa"] = df.apply(
            lambda row: calc_cpa(row.get("cost", 0), row.get("conversions", 0)), 
            axis=1
        )
    
    if "revenue" in df.columns and "cost" in df.columns:
        df["roas"] = df.apply(
            lambda row: calc_roas(row.get("revenue", 0), row.get("cost", 0)), 
            axis=1
        )
    
    return df
