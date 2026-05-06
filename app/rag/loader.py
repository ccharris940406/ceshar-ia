from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).parent.parent.parent / "documentation"

_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def load_documents() -> list[Document]:
    loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
        silent_errors=True,
    )
    docs = loader.load()
    return _splitter.split_documents(docs)
