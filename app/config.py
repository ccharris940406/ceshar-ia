import os

from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

    def _get_config(self, provider: str, suffix: str):
        prefix = provider.upper()
        return os.getenv(f"{prefix}_{suffix}")

    def get_llm_config(self):
        api_key = self._get_config(self.llm_provider, "API_KEY")
        model = self._get_config(self.llm_provider, "MODEL")
        embedding_api_key = self._get_config(self.embedding_provider, "API_KEY")
        embedding_model = self._get_config(self.embedding_provider, "EMBEDDING_MODEL")

        if not api_key or not model:
            raise ValueError(f"LLM configuration for {self.llm_provider} is incomplete")
        if not embedding_api_key or not embedding_model:
            raise ValueError(f"Embedding configuration for {self.embedding_provider} is incomplete")

        return {
            "provider": self.llm_provider,
            "api_key": api_key,
            "model": model,
            "embedding_provider": self.embedding_provider,
            "embedding_api_key": embedding_api_key,
            "embedding_model": embedding_model,
        }


config = Config()
