"""Script para levantar la API."""
import uvicorn
from src.config import settings

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host=settings.api_host, port=settings.api_port, reload=settings.api_debug)
