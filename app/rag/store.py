from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma

from app.factory.embeddings import embeddings_factory
from app.rag.loader import load_documents
from app.rag.rerank import RerankingRetriever, make_reranking_retriever

STORE_PATH = Path(__file__).parent.parent.parent / "data" / "chroma_store"
_COLLECTION = "ceshar_docs"


def _make_client() -> chromadb.ClientAPI:
    STORE_PATH.mkdir(parents=True, mode=0o755, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(STORE_PATH),
        settings=Settings(anonymized_telemetry=False, allow_reset=True),
    )


def _create_store(client: chromadb.ClientAPI) -> Chroma:
    docs = load_documents()
    return Chroma.from_documents(
        docs,
        embeddings_factory.get_embeddings(),
        client=client,
        collection_name=_COLLECTION,
    )


def get_retriever() -> RerankingRetriever:
    client = _make_client()
    existing = [c.name for c in client.list_collections()]

    if _COLLECTION in existing:
        store = Chroma(
            client=client,
            collection_name=_COLLECTION,
            embedding_function=embeddings_factory.get_embeddings(),
        )
    else:
        store = _create_store(client)

    return make_reranking_retriever(store)


def rebuild_store() -> RerankingRetriever:
    client = _make_client()
    try:
        client.delete_collection(_COLLECTION)
    except Exception:
        pass
    store = _create_store(client)
    return make_reranking_retriever(store)
