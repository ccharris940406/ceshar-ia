from fastapi import APIRouter, HTTPException

from app.agents.chat import ChatAgent
from app.api.schemas import ChatRequest, ChatResponse, HistoryResponse, MessageSchema

router = APIRouter(prefix="/chat", tags=["chat"])

_sessions: dict[str, ChatAgent] = {}


def _get_agent(session_id: str) -> ChatAgent:
    if session_id not in _sessions:
        _sessions[session_id] = ChatAgent()
    return _sessions[session_id]


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    agent = _get_agent(request.session_id)
    response = agent.chat(request.message)
    return ChatResponse(response=response, session_id=request.session_id)


@router.get("/{session_id}/history", response_model=HistoryResponse)
async def get_history(session_id: str) -> HistoryResponse:
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = _sessions[session_id]
    messages = [
        MessageSchema(role=msg.type, content=str(msg.content))
        for msg in agent.history
        if msg.type in ("human", "ai")
    ]
    return HistoryResponse(session_id=session_id, messages=messages)
