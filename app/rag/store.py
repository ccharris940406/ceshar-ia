from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from app.factory.embeddings import embeddings_factory
from app.rag.loader import load_documents

STORE_PATH = Path(__file__).parent.parent.parent / "data" / "chroma_store"


def _build_and_save() -> Chroma:
    docs = load_documents()
    return Chroma.from_documents(
        docs,
        embeddings_factory.get_embeddings(),
        persist_directory=str(STORE_PATH),
    )


def get_retriever() -> VectorStoreRetriever:
    embeddings = embeddings_factory.get_embeddings()

    if STORE_PATH.exists() and any(STORE_PATH.iterdir()):
        store = Chroma(
            persist_directory=str(STORE_PATH),
            embedding_function=embeddings,
        )
    else:
        store = _build_and_save()

    return store.as_retriever(search_kwargs={"k": 4})
