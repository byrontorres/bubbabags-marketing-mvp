"""Configuracion centralizada del proyecto."""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # Google Cloud
    gcp_project_id: str = Field(default="bubbabags-mmg", alias="GCP_PROJECT_ID")
    bq_dataset: str = Field(default="production_bubbabags", alias="BQ_DATASET")
    google_credentials: str | None = Field(default=None, alias="GOOGLE_APPLICATION_CREDENTIALS")
    
    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    llm_temperature: float = Field(default=0.1, alias="LLM_TEMPERATURE")
    
    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_debug: bool = Field(default=True, alias="API_DEBUG")
    
    # Streamlit
    streamlit_port: int = Field(default=8501, alias="STREAMLIT_PORT")
    
    # Modelo
    model_path: str = Field(default="src/modeling/artifacts/roas_model.joblib", alias="MODEL_PATH")
    model_version: str = Field(default="1.0.0", alias="MODEL_VERSION")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
