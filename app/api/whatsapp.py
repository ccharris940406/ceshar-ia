from fastapi import APIRouter, Form
from fastapi.responses import Response

from app.agents.chat import ChatAgent

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

_sessions: dict[str, ChatAgent] = {}


def _get_agent(session_id: str) -> ChatAgent:
    if session_id not in _sessions:
        _sessions[session_id] = ChatAgent()
    return _sessions[session_id]


@router.post("")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
) -> Response:
    agent = _get_agent(From)
    message = await agent.chat(Body)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""
    return Response(content=twiml, media_type="text/xml")
