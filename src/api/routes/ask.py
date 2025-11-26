"""Endpoint para preguntas."""
from fastapi import APIRouter, HTTPException
from src.api.schemas import AskRequest, AskResponse
from src.agent.chain import get_agent

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_agent(request: AskRequest):
    try:
        agent = get_agent()
        result = agent.ask(request.question)
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
