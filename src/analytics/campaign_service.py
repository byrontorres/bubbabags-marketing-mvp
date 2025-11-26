"""Servicio de campanas."""
import pandas as pd
from src.data.bigquery_client import execute_query
from src.analytics.metrics import add_metrics_to_dataframe
from src.config import settings


def get_top_campaigns(start_date: str, end_date: str, metric: str = "roas", limit: int = 10) -> pd.DataFrame:
    query = f"""
    SELECT *
    FROM `{settings.gcp_project_id}.{settings.bq_dataset}.v_campaign_performance_daily`
    WHERE date BETWEEN '{start_date}' AND '{end_date}'
    """
    
    df = execute_query(query)
    
    if df.empty:
        return df
    
    df = add_metrics_to_dataframe(df)
    
    agg_df = df.groupby(["campaign_id", "campaign_name", "channel"]).agg({
        "impressions": "sum",
        "clicks": "sum",
        "cost": "sum",
        "conversions": "sum",
        "revenue": "sum"
    }).reset_index()
    
    agg_df = add_metrics_to_dataframe(agg_df)
    
    if metric in agg_df.columns:
        agg_df = agg_df.sort_values(metric, ascending=False).head(limit)
    
    return agg_df


def get_performance_by_channel(start_date: str, end_date: str) -> pd.DataFrame:
    query = f"""
    SELECT 
        channel,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        SUM(cost) as cost,
        SUM(conversions) as conversions,
        SUM(revenue) as revenue
    FROM `{settings.gcp_project_id}.{settings.bq_dataset}.v_campaign_performance_daily`
    WHERE date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY channel
    ORDER BY cost DESC
    """
    
    df = execute_query(query)
    
    if not df.empty:
        df = add_metrics_to_dataframe(df)
    
    return df
