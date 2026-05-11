from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage

from app.factory.llm import llm_factory

_SCOPE_PROMPT = """You are a helpful assistant that helps the user determine the scope of a project.
Respond only with Yes or No"""


async def is_in_scope(user_input: str) -> bool:
    llm = llm_factory.get_llm()
    result = await llm.ainvoke(
        [SystemMessage(content=_SCOPE_PROMPT), HumanMessage(content=user_input)]
    )

    return str(result.content).strip().lower() == "yes"
