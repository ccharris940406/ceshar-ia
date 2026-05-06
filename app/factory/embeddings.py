from typing import Callable

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from app.config import config

_BuilderFn = Callable[[str, str], Embeddings]

_PROVIDERS: dict[str, _BuilderFn] = {
    "openai": lambda key, model: OpenAIEmbeddings(  # pyright: ignore[reportCallIssue]
        api_key=SecretStr(key), model=model
    ),
    "deepseek": lambda key, model: OpenAIEmbeddings(  # pyright: ignore[reportCallIssue]
        api_key=SecretStr(key), model=model, base_url="https://api.deepseek.com"
    ),
    "fastembed": lambda _key, model: FastEmbedEmbeddings(model_name=model),  # pyright: ignore[reportCallIssue]
}


class EmbeddingsFactory:
    def __init__(self):
        self._config = config.get_llm_config()

    def get_embeddings(self) -> Embeddings:
        provider = self._config["embedding_provider"]
        builder = _PROVIDERS.get(provider)

        if not builder:
            raise ValueError(f"Unsupported embedding provider: {provider}")

        return builder(self._config["embedding_api_key"], self._config["embedding_model"])


embeddings_factory = EmbeddingsFactory()
