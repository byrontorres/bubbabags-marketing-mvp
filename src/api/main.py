"""FastAPI - Aplicacion principal."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import ask, predict, campaigns, health

app = FastAPI(
    title="Bubbabags Marketing Intelligence API",
    description="API para el agente conversacional de marketing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(ask.router, tags=["Agent"])
app.include_router(predict.router, tags=["Prediction"])
app.include_router(campaigns.router, tags=["Campaigns"])


@app.get("/")
async def root():
    return {"message": "Bubbabags Marketing Intelligence API", "docs": "/docs"}
