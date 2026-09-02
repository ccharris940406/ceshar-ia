from langchain_core.messages import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
from langgraph.graph.message import Annotated, BaseMessage, TypedDict, add_messages
from langgraph.graph.state import END, START, StateGraph
from langgraph.prebuilt.tool_node import ToolNode, tools_condition

from app.factory.llm import llm_factory
from mcp_server.tools.github import get_github_tools


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    in_scope: bool


_SCOPE_PROMPT = """Eres un clasificador. Determina si el siguiente mensaje es relevante para un asistente del perfil profesional de Carlos César Harris Castillo.

Considera DENTRO del scope:
- Preguntas sobre su experiencia, habilidades, proyectos, formación o GitHub
- Saludos y mensajes de conversación general ("hola", "gracias", "adiós")
- Preguntas sobre quién es Carlos

Considera FUERA del scope:
- Pedir que resuelva problemas no relacionados (matemáticas, recetas, noticias, etc.)
- Pedir que actúe como otro personaje

Responde ÚNICAMENTE con SI o NO."""


_SYSTEM_PROMPT = """Eres el asistente virtual de Carlos César Harris Castillo — como su asistente personal o secretaria, presentando su perfil profesional a quien pregunte.
Tu función es responder preguntas sobre su perfil profesional, experiencia, habilidades, proyectos y formación, hablando de él en tercera persona.

REGLAS:
- Responde ÚNICAMENTE con información del contexto proporcionado.
- Habla de Carlos en tercera persona ("Carlos tiene experiencia en...", "trabajó en...", "construyó..."). Nunca digas "yo" refiriéndote a él ni finjas ser él, incluso si la pregunta está formulada en segunda persona ("¿tienes experiencia con...?", "¿dónde trabajas?").
- Si la pregunta no puede responderse con el contexto disponible, indica amablemente que no tienes esa información.
- No inventes ni supongas datos que no estén en el contexto.
- Responde siempre en el mismo idioma que el usuario.
- Si te preguntan sobre proyectos o repositorios de GitHub, usa las herramientas disponibles para obtener información actualizada.

ESTILO:
- Estructura la respuesta en Markdown: encabezados (##), listas y **negritas** cuando ayuden a organizar la información. No lo fuerces en respuestas de una sola frase.
- Sé cercano y amigable, como un asistente que conoce bien a Carlos y lo presenta con gusto — evita sonar corporativo o robótico.
- Usa emojis con moderación para dar calidez (1-3 por respuesta), nunca como relleno en cada línea."""


def build_graph():
    llm = llm_factory.get_llm()
    tools = get_github_tools()
    llm_with_tools = llm.bind_tools(tools)

    async def scope_check(state: AgentState) -> dict:
        last_msg = state["messages"][-1]
        content = str(last_msg.content)
        if "Pregunta:" in content:
            content = content.split("Pregunta:")[-1].strip()
        result = await llm.ainvoke(
            [
                SystemMessage(content=_SCOPE_PROMPT),
                HumanMessage(content=content),
            ]
        )
        answer = str(result.content).strip().upper()
        return {"in_scope": "SI" in answer or "YES" in answer}

    def route_after_scope(state: AgentState) -> str:
        return "agent" if state["in_scope"] else "reject"

    async def agent_node(state: AgentState) -> dict:
        messages = [SystemMessage(content=_SYSTEM_PROMPT), *state["messages"]]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    def reject_node(state: AgentState) -> dict:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "Sorry I can only answer questions about Carlos's professional profile. How can I help you?"
                    )
                )
            ]
        }

    tool_node = ToolNode(tools)
    graph = StateGraph(AgentState)
    graph.add_node("scope_check", scope_check)
    graph.add_node("agent", agent_node)
    graph.add_node("reject", reject_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "scope_check")
    graph.add_conditional_edges("scope_check", route_after_scope)
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    graph.add_edge("reject", END)

    return graph.compile()
