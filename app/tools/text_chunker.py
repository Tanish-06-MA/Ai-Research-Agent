from h11._abnf import chunk_size
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str) -> str:
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

    chunks = splitter.split_text(text)
    return chunks
