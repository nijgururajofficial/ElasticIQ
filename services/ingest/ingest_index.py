"""
Ingest pipeline:
- extract text from uploaded files (PDF/DOCX/TXT)
- chunk into passages
- call Vertex Embeddings for each chunk -> embedding vector (placeholder)
- index into Elastic with fields: doc_id, chunk_id, text, embedding, metadata
"""

import os
import uuid
from typing import Dict, List

import numpy as np
import logging
from docx import Document as DocxDocument
from elasticsearch import Elasticsearch
from pdfminer.high_level import extract_text as extract_pdf_text
from PyPDF2 import PdfReader
from dotenv import load_dotenv, find_dotenv

from ..common.vertex import call_vertex_embeddings


load_dotenv(find_dotenv(), override=False)

# --- CONFIG (replace) ---
ELASTIC_URL = os.environ.get("ELASTIC_URL", "http://localhost:9200")
ELASTIC_API_KEY = os.environ.get("ELASTIC_API_KEY")
ELASTIC_USER = os.environ.get("ELASTIC_USER", "")
ELASTIC_PASS = os.environ.get("ELASTIC_PASS", "")
INDEX_NAME = os.environ.get("ELASTIC_INDEX", "docs_index_v1")
GCS_BUCKET = os.environ.get("GCS_BUCKET", "my-bucket")
VERTEX_PROJECT = os.environ.get("VERTEX_PROJECT", "your-gcp-project")
VERTEX_LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")
VERTEX_EMBEDDING_MODEL = os.environ.get(
    "VERTEX_EMBEDDING_MODEL", " << REPLACE_WITH_MODEL >> "
)  # e.g. "textembedding-gecko"
VERTEX_EMBEDDING_DIMS = int(os.environ.get("VERTEX_EMBEDDING_DIMS", "768"))
# -------------------------

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

if ELASTIC_API_KEY:
    es = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY)
else:
    es = Elasticsearch(ELASTIC_URL, basic_auth=(ELASTIC_USER, ELASTIC_PASS))


def extract_text_from_pdf(path: str) -> str:
    text = extract_pdf_text(path)
    if text.strip():
        return text

    try:
        reader = PdfReader(path)
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
        return "\n".join(pages_text)
    except Exception:
        return text


def extract_text_from_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


def get_vertex_embeddings(texts: List[str]) -> List[List[float]]:
    """Fetch embeddings for the provided texts using Vertex AI."""
    if not texts:
        return []

    embeddings = call_vertex_embeddings(
        project=VERTEX_PROJECT,
        location=VERTEX_LOCATION,
        model=VERTEX_EMBEDDING_MODEL,
        texts=texts,
    )
    return embeddings
def ensure_index():
    recreate = False
    if es.indices.exists(index=INDEX_NAME):
        mapping = es.indices.get_mapping(index=INDEX_NAME)
        current_dims = (
            mapping.get(INDEX_NAME, {})
            .get("mappings", {})
            .get("properties", {})
            .get("embedding", {})
            .get("dims")
        )
        if current_dims and current_dims != VERTEX_EMBEDDING_DIMS:
            logger.warning(
                "Recreating index %s due to embedding dim mismatch (current=%s, expected=%s)",
                INDEX_NAME,
                current_dims,
                VERTEX_EMBEDDING_DIMS,
            )
            es.indices.delete(index=INDEX_NAME)
            recreate = True
        else:
            return
    else:
        recreate = True

    if recreate:
        mapping = {
            "mappings": {
                "properties": {
                    "doc_id": {"type": "keyword"},
                    "chunk_id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "text": {"type": "text"},
                    "metadata": {"type": "object"},
                    "embedding": {"type": "dense_vector", "dims": VERTEX_EMBEDDING_DIMS},
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=mapping)


def index_document(file_path: str, title: str, metadata: Dict[str, str]):
    ensure_index()
    text = ""
    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    if not text or not text.strip():
        raise ValueError("Document contains no extractable text")

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Document contains no extractable text")
    embeddings = get_vertex_embeddings(chunks)

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            f"Embedding count {len(embeddings)} did not match chunk count {len(chunks)}"
        )

    doc_id = str(uuid.uuid4())
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        doc = {
            "doc_id": doc_id,
            "chunk_id": f"{doc_id}_{idx}",
            "title": title,
            "text": chunk,
            "metadata": metadata,
            "embedding": emb,
        }
        es.index(index=INDEX_NAME, id=doc["chunk_id"], document=doc)
    print(f"Indexed {len(chunks)} chunks for document {title}")


if __name__ == "__main__":
    ensure_index()
    # quick local test: index a sample file
    sample_file = "sample_data/example.pdf"
    index_document(sample_file, title="Example PDF", metadata={"source": "demo"})

