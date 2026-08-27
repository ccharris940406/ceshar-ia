import re

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.store.base.embed import AEmbeddingsFunc
from openai import responses

from app.agents.graph import build_graph
from app.factory.llm import llm_factory
from app.rag.rerank import RerankingRetriever
from app.rag.store import get_retriever
from mcp_server.tools.github import get_github_tools

_INJECTION_PATTERNS = [
    r"ignora\s+(todo\s+)?(lo\s+)?anterior",
    r"olvida\s+(tus\s+)?(instrucciones|reglas|sistema)",
    r"nuevo\s+prompt",
    r"actúa\s+como\s+(?!carlos)",
    r"actua\s+como\s+(?!carlos)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"forget\s+(your\s+)?(instructions|rules|system)",
    r"\[system\]",
    r"<system>",
    r"jailbreak",
    r"do\s+anything\s+now",
    r"\bdan\b.*modo",
    r"override\s+(your\s+)?(instructions|system)",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

_REJECTION_MSG = (
    "Solo puedo responder preguntas sobre el perfil profesional de Carlos. "
    "¿En qué te puedo ayudar?"
)


def _is_injection(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED_PATTERNS)


_SYSTEM_PROMPT = """Eres el asistente virtual de Carlos César Harris Castillo — como su asistente personal o secretaria, presentando su perfil profesional a quien pregunte.
Tu función es responder preguntas sobre su perfil profesional, experiencia, habilidades, proyectos y formación, hablando de él en tercera persona.

REGLAS:
- Responde ÚNICAMENTE con información del contexto proporcionado.
- Habla de Carlos en tercera persona ("Carlos tiene experiencia en...", "trabajó en...", "construyó..."). Nunca digas "yo" refiriéndote a él ni finjas ser él.
- Si la pregunta no puede responderse con el contexto disponible, indica amablemente que no tienes esa información.
- No inventes ni supongas datos que no estén en el contexto.
- Responde siempre en el mismo idioma que el usuario.
- Si te preguntan sobre proyectos o repositorios de GitHub, usa herramientas disponibles para obtener información actualizada.

ESTILO:
- Estructura la respuesta en Markdown: encabezados (##), listas y **negritas** cuando ayuden a organizar la información. No lo fuerces en respuestas de una sola frase.
- Sé cercano y amigable, como un asistente que conoce bien a Carlos y lo presenta con gusto — evita sonar corporativo o robótico.
- Usa emojis con moderación para dar calidez (1-3 por respuesta), nunca como relleno en cada línea."""


class ChatAgent:
    def __init__(self):
        self.llm = llm_factory.get_llm()
        self.retriever: RerankingRetriever = get_retriever()
        self.graph = build_graph()
        self.history: list[BaseMessage] = []

    def refresh_retriever(self, retriever: RerankingRetriever) -> None:
        self.retriever = retriever

    async def chat(self, user_input: str) -> str:
        if _is_injection(user_input):
            return _REJECTION_MSG

        docs = await self.retriever.ainvoke(user_input)
        if docs:
            context = "\n\n".join(doc.page_content for doc in docs)
            message = f"Contexto:\n{context}\n\nPregunta:\n{user_input}"
        else:
            message = user_input

        result = await self.graph.ainvoke(
            {"messages": [*self.history, HumanMessage(content=message)]}  # type: ignore[call-arg]
        )

        response = str(result["messages"][-1].content)

        self.history.append(HumanMessage(content=user_input))
        self.history.append(AIMessage(content=response))

        return response
