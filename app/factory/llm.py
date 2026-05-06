from typing import Callable

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.config import config

_BuilderFn = Callable[[str, str], BaseChatModel]

_PROVIDERS: dict[str, _BuilderFn] = {
    "openai": lambda key, model: ChatOpenAI(  # pyright: ignore[reportCallIssue]
        api_key=SecretStr(key), model=model
    ),
    "anthropic": lambda key, model: ChatAnthropic(  # pyright: ignore[reportCallIssue]
        api_key=SecretStr(key), model_name=model
    ),
    "deepseek": lambda key, model: ChatOpenAI(  # pyright: ignore[reportCallIssue]
        api_key=SecretStr(key), model=model, base_url="https://api.deepseek.com"
    ),
}


class LLMFactory:
    def __init__(self):
        self.llm_config = config.get_llm_config()

    def get_llm(self):
        provider = self.llm_config["provider"]
        builder = _PROVIDERS.get(provider)

        if not builder:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        return builder(self.llm_config["api_key"], self.llm_config["model"])


llm_factory = LLMFactory()
