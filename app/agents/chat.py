from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.vectorstores import VectorStoreRetriever

from app.factory.llm import llm_factory
from app.rag.store import get_retriever

_SYSTEM_PROMPT = """Eres un asistente personal de Carlos César Harris Castillo.
Tu función es responder preguntas sobre su perfil profesional, experiencia, habilidades, proyectos y formación.

REGLAS:
- Responde ÚNICAMENTE con información del contexto proporcionado.
- Si la pregunta no puede responderse con el contexto disponible, indica amablemente que no tienes esa información.
- No inventes ni supongas datos que no estén en el contexto.
- Responde siempre en el mismo idioma que el usuario."""


class ChatAgent:
    def __init__(self):
        self.llm = llm_factory.get_llm()
        self.retriever: VectorStoreRetriever = get_retriever()
        self.history: list[BaseMessage] = [SystemMessage(content=_SYSTEM_PROMPT)]

    def refresh_retriever(self, retriever: VectorStoreRetriever) -> None:
        self.retriever = retriever

    def chat(self, user_input: str) -> str:
        docs = self.retriever.invoke(user_input)

        if docs:
            context = "\n\n".join(doc.page_content for doc in docs)
            human_msg = HumanMessage(content=f"Contexto:\n{context}\n\nPregunta: {user_input}")
        else:
            human_msg = HumanMessage(content=user_input)

        response: AIMessage = self.llm.invoke([*self.history, human_msg])  # type: ignore[assignment]

        self.history.append(HumanMessage(content=user_input))
        self.history.append(response)

        return str(response.content)
