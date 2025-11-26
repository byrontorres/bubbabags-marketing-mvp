"""Cliente de BigQuery."""
from google.cloud import bigquery
import pandas as pd
from functools import lru_cache
from src.config import settings


@lru_cache()
def get_bigquery_client() -> bigquery.Client:
    return bigquery.Client(project=settings.gcp_project_id)


def execute_query(query: str) -> pd.DataFrame:
    client = get_bigquery_client()
    return client.query(query).to_dataframe()


def execute_query_to_dict(query: str) -> list[dict]:
    df = execute_query(query)
    return df.to_dict(orient="records")


def get_table_ref(table_name: str) -> str:
    return f"{settings.gcp_project_id}.{settings.bq_dataset}.{table_name}"


def list_tables() -> list[str]:
    client = get_bigquery_client()
    dataset_ref = bigquery.DatasetReference(settings.gcp_project_id, settings.bq_dataset)
    tables = list(client.list_tables(dataset_ref))
    return [t.table_id for t in tables]


def test_connection() -> bool:
    try:
        client = get_bigquery_client()
        result = client.query("SELECT 1 as test").to_dataframe()
        return len(result) > 0
    except Exception as e:
        print(f"Error de conexion: {e}")
        return False
