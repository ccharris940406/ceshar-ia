import asyncio
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from pydantic import BaseModel, ConfigDict, Field, SecretStr

_RERANK_MODEL = "claude-haiku-4-5-20251001"

_SCORE_PROMPT = (
    "Pregunta del usuario:\n{query}\n\n"
    "Fragmento candidato:\n{document}\n\n"
    "Califica de 0 a 10 qué tan bien este fragmento responde la pregunta "
    "(10 = respuesta directa y completa, 0 = sin relación)."
)


class _RelevanceScore(BaseModel):
    score: float = Field(description="Relevancia del fragmento respecto a la pregunta, de 0 a 10.")


_scorer = None


def _get_scorer():
    global _scorer
    if _scorer is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY es requerida para el reranking")
        llm = ChatAnthropic(api_key=SecretStr(api_key), model_name=_RERANK_MODEL, temperature=0)  # pyright: ignore[reportCallIssue]
        _scorer = llm.with_structured_output(_RelevanceScore)
    return _scorer


class RerankingRetriever(BaseRetriever):
    """Retrieves a wide candidate set by similarity, then scores each
    candidate's relevance to the query independently with an LLM judge and
    keeps only the top `top_n`. Pointwise LLM scoring reads query and
    document together, so it ranks relevance far more precisely than
    embedding similarity alone — which only compares each side in
    isolation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_retriever: VectorStoreRetriever
    top_n: int = 4

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        candidates = self.base_retriever.invoke(query)
        if not candidates:
            return []

        scorer = _get_scorer()
        scores = [
            scorer.invoke(_SCORE_PROMPT.format(query=query, document=doc.page_content)).score  # type: ignore[union-attr]
            for doc in candidates
        ]
        ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
        return [doc for doc, _ in ranked[: self.top_n]]

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> list[Document]:
        candidates = await self.base_retriever.ainvoke(query)
        if not candidates:
            return []

        scorer = _get_scorer()
        results = await asyncio.gather(
            *[
                scorer.ainvoke(_SCORE_PROMPT.format(query=query, document=doc.page_content))
                for doc in candidates
            ]
        )
        scores = [result.score for result in results]  # type: ignore[union-attr]
        ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
        return [doc for doc, _ in ranked[: self.top_n]]


def make_reranking_retriever(
    store: VectorStore, *, fetch_k: int = 15, top_n: int = 4
) -> RerankingRetriever:
    base_retriever = store.as_retriever(search_kwargs={"k": fetch_k})
    return RerankingRetriever(base_retriever=base_retriever, top_n=top_n)
