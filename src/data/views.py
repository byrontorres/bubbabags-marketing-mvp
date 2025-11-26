"""Queries que simulan las vistas SQL (sin necesidad de crearlas en BigQuery)."""
from src.data.bigquery_client import execute_query
from src.config import settings
import pandas as pd

PROJECT = settings.gcp_project_id
DATASET = settings.bq_dataset


def get_campaign_performance_daily(start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Vista unificada de rendimiento diario de campanas."""
    
    where_clause = ""
    if start_date and end_date:
        where_clause = f"WHERE date BETWEEN '{start_date}' AND '{end_date}'"
    
    query = f"""
    SELECT * FROM (
        SELECT 
            event_date as date,
            CAST(campaign_id AS STRING) as campaign_id,
            campaign_name,
            'google_ads' as channel,
            campaign_status,
            device,
            COALESCE(impressions, 0) as impressions,
            COALESCE(clicks, 0) as clicks,
            COALESCE(cost_micros, 0) / 1000000 as cost,
            COALESCE(conversions, 0) as conversions,
            COALESCE(conversions_value, 0) as revenue,
            SAFE_DIVIDE(COALESCE(conversions_value, 0), COALESCE(cost_micros, 0) / 1000000) as roas
        FROM `{PROJECT}.{DATASET}.gads_campaign`
        WHERE event_date IS NOT NULL

        UNION ALL

        SELECT 
            date_start as date,
            CAST(campaign_id AS STRING) as campaign_id,
            campaign_name,
            'meta_ads' as channel,
            'ENABLED' as campaign_status,
            device_platform as device,
            COALESCE(CAST(impressions AS INT64), 0) as impressions,
            COALESCE(CAST(clicks AS INT64), 0) as clicks,
            COALESCE(spend, 0) as cost,
            0 as conversions,
            COALESCE(spend, 0) * COALESCE(purchase_roas[SAFE_OFFSET(0)].value, 0) as revenue,
            COALESCE(purchase_roas[SAFE_OFFSET(0)].value, 0) as roas
        FROM `{PROJECT}.{DATASET}.meta_ads_insights_daily`
        WHERE date_start IS NOT NULL
    )
    {where_clause}
    ORDER BY date DESC
    """
    return execute_query(query)


def get_campaign_performance_monthly(start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Rendimiento mensual de campanas."""
    
    where_clause = "WHERE cost > 0"
    if start_date and end_date:
        where_clause = f"WHERE date BETWEEN '{start_date}' AND '{end_date}'"
    
    query = f"""
    SELECT
        FORMAT_DATE('%Y-%m', date) as month,
        campaign_id,
        campaign_name,
        channel,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        SUM(cost) as cost,
        SUM(conversions) as conversions,
        SUM(revenue) as revenue,
        SAFE_DIVIDE(SUM(clicks), SUM(impressions)) as ctr,
        SAFE_DIVIDE(SUM(cost), SUM(clicks)) as cpc,
        SAFE_DIVIDE(SUM(revenue), SUM(cost)) as roas
    FROM (
        SELECT 
            event_date as date,
            CAST(campaign_id AS STRING) as campaign_id,
            campaign_name,
            'google_ads' as channel,
            COALESCE(impressions, 0) as impressions,
            COALESCE(clicks, 0) as clicks,
            COALESCE(cost_micros, 0) / 1000000 as cost,
            COALESCE(conversions, 0) as conversions,
            COALESCE(conversions_value, 0) as revenue
        FROM `{PROJECT}.{DATASET}.gads_campaign`
        WHERE event_date IS NOT NULL

        UNION ALL

        SELECT 
            date_start as date,
            CAST(campaign_id AS STRING) as campaign_id,
            campaign_name,
            'meta_ads' as channel,
            COALESCE(CAST(impressions AS INT64), 0) as impressions,
            COALESCE(CAST(clicks AS INT64), 0) as clicks,
            COALESCE(spend, 0) as cost,
            0 as conversions,
            COALESCE(spend, 0) * COALESCE(purchase_roas[SAFE_OFFSET(0)].value, 0) as revenue
        FROM `{PROJECT}.{DATASET}.meta_ads_insights_daily`
        WHERE date_start IS NOT NULL
    )
    {where_clause}
    GROUP BY month, campaign_id, campaign_name, channel
    ORDER BY month DESC, cost DESC
    """
    return execute_query(query)


def get_channel_summary() -> pd.DataFrame:
    """Resumen por canal (Google Ads vs Meta Ads)."""
    
    query = f"""
    SELECT
        channel,
        COUNT(DISTINCT campaign_id) as total_campaigns,
        SUM(impressions) as total_impressions,
        SUM(clicks) as total_clicks,
        SUM(cost) as total_cost,
        SUM(conversions) as total_conversions,
        SUM(revenue) as total_revenue,
        SAFE_DIVIDE(SUM(clicks), SUM(impressions)) as avg_ctr,
        SAFE_DIVIDE(SUM(cost), SUM(clicks)) as avg_cpc,
        SAFE_DIVIDE(SUM(revenue), SUM(cost)) as avg_roas
    FROM (
        SELECT 
            CAST(campaign_id AS STRING) as campaign_id,
            'google_ads' as channel,
            COALESCE(impressions, 0) as impressions,
            COALESCE(clicks, 0) as clicks,
            COALESCE(cost_micros, 0) / 1000000 as cost,
            COALESCE(conversions, 0) as conversions,
            COALESCE(conversions_value, 0) as revenue
        FROM `{PROJECT}.{DATASET}.gads_campaign`

        UNION ALL

        SELECT 
            CAST(campaign_id AS STRING) as campaign_id,
            'meta_ads' as channel,
            COALESCE(CAST(impressions AS INT64), 0) as impressions,
            COALESCE(CAST(clicks AS INT64), 0) as clicks,
            COALESCE(spend, 0) as cost,
            0 as conversions,
            COALESCE(spend, 0) * COALESCE(purchase_roas[SAFE_OFFSET(0)].value, 0) as revenue
        FROM `{PROJECT}.{DATASET}.meta_ads_insights_daily`
    )
    GROUP BY channel
    """
    return execute_query(query)


def get_roas_training_dataset(lookback_days: int = 90) -> pd.DataFrame:
    """Dataset para entrenar modelo de prediccion de ROAS."""
    
    query = f"""
    SELECT
        date,
        campaign_id,
        campaign_name,
        channel,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        SUM(cost) as cost,
        SUM(conversions) as conversions,
        SUM(revenue) as revenue,
        SAFE_DIVIDE(SUM(clicks), SUM(impressions)) as ctr,
        SAFE_DIVIDE(SUM(cost), SUM(clicks)) as cpc,
        SAFE_DIVIDE(SUM(conversions), SUM(clicks)) as conversion_rate,
        SAFE_DIVIDE(SUM(revenue), SUM(cost)) as roas,
        EXTRACT(DAYOFWEEK FROM date) as day_of_week,
        CASE WHEN EXTRACT(DAYOFWEEK FROM date) IN (1, 7) THEN 1 ELSE 0 END as is_weekend,
        EXTRACT(MONTH FROM date) as month
    FROM (
        SELECT 
            event_date as date,
            CAST(campaign_id AS STRING) as campaign_id,
            campaign_name,
            'google_ads' as channel,
            COALESCE(impressions, 0) as impressions,
            COALESCE(clicks, 0) as clicks,
            COALESCE(cost_micros, 0) / 1000000 as cost,
            COALESCE(conversions, 0) as conversions,
            COALESCE(conversions_value, 0) as revenue
        FROM `{PROJECT}.{DATASET}.gads_campaign`
        WHERE event_date IS NOT NULL
          AND event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days} DAY)

        UNION ALL

        SELECT 
            date_start as date,
            CAST(campaign_id AS STRING) as campaign_id,
            campaign_name,
            'meta_ads' as channel,
            COALESCE(CAST(impressions AS INT64), 0) as impressions,
            COALESCE(CAST(clicks AS INT64), 0) as clicks,
            COALESCE(spend, 0) as cost,
            0 as conversions,
            COALESCE(spend, 0) * COALESCE(purchase_roas[SAFE_OFFSET(0)].value, 0) as revenue
        FROM `{PROJECT}.{DATASET}.meta_ads_insights_daily`
        WHERE date_start IS NOT NULL
          AND date_start >= DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days} DAY)
    )
    WHERE cost > 0
    GROUP BY date, campaign_id, campaign_name, channel
    """
    return execute_query(query)