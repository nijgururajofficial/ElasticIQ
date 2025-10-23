import os
from typing import Dict, List, Optional

from dotenv import load_dotenv, find_dotenv
from elasticsearch import Elasticsearch
from fastapi import Body, FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import uuid
from elasticsearch.exceptions import NotFoundError

# Update imports to use full package path
from services.common.vertex import (
    call_vertex_embeddings,
    call_vertex_text_generation,
)
from services.ingest.ingest_index import index_document
from services.common.health import run_readiness_checks, is_system_ready


load_dotenv(find_dotenv(), override=True)

app = FastAPI()

# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

ELASTIC_URL = os.environ.get("ELASTIC_URL", "http://localhost:9200")
ELASTIC_API_KEY = os.environ.get("ELASTIC_API_KEY")
ELASTIC_USER = os.environ.get("ELASTIC_USER")
ELASTIC_PASS = os.environ.get("ELASTIC_PASS")
INDEX_NAME = os.environ.get("ELASTIC_INDEX", "docs_index_v1")

if ELASTIC_API_KEY:
    es = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY)
else:
    es = Elasticsearch(ELASTIC_URL, basic_auth=(ELASTIC_USER or "", ELASTIC_PASS or ""))


def embed_query(query: str) -> List[float]:
    embeddings = call_vertex_embeddings(
        project=os.environ.get("VERTEX_PROJECT", ""),
        location=os.environ.get("VERTEX_LOCATION", "us-central1"),
        model=os.environ.get("VERTEX_EMBEDDING_MODEL", ""),
        texts=[query],
    )
    if not embeddings:
        return []
    return embeddings[0]


def hybrid_search(query: str, top_k: int = 5, alpha: float = 0.5):
    """
    Hybrid search approach:
    - BM25 (text) and vector similarity (cosine) combined via should clauses & script_score
    - alpha: weight for vector vs text (0..1). This is an example; tune per corpus.
    """
    if not es.indices.exists(index=INDEX_NAME):
        return []
    query_vector = embed_query(query)  # list of floats

    text_query = {
        "bool": {
            "should": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["text^2", "title^3"],
                    }
                }
            ]
        }
    }

    if not query_vector:
        es_query = {
            "size": top_k,
            "query": text_query,
            "_source": ["doc_id", "chunk_id", "title", "text", "metadata"],
        }
    else:
        es_query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": text_query,
                    "script": {
                        "source": """
                            double bm25 = _score;
                            double vectorScore = cosineSimilarity(params.query_vector, 'embedding');
                            if (Double.isNaN(vectorScore)) {
                                vectorScore = 0;
                            }
                            double normalizedVector = (vectorScore + 1.0) / 2.0;
                            return ((1 - params.alpha) * bm25) + (params.alpha * normalizedVector);
                        """,
                        "params": {"query_vector": query_vector, "alpha": alpha},
                    },
                }
            },
            "_source": ["doc_id", "chunk_id", "title", "text", "metadata"],
        }
    try:
        res = es.search(index=INDEX_NAME, body=es_query)
    except NotFoundError:
        return []
    hits = [hit["_source"] for hit in res["hits"]["hits"]]
    return hits


def call_vertex_rag(prompt: str, contexts: List[Dict]) -> str:
    """
    Build final RAG prompt and call Vertex Text Generation (Gemini/Text Gen).
    contexts: list of retrieved text snippets + metadata.
    """
    system_prompt = (
        "You are an assistant answering user queries using the provided document snippets. "
        "Always provide complete, well-structured answers. "
        "Cite the source (title and chunk_id) where relevant. "
        "If information is not found in the snippets, clearly state that. "
        "End all responses with a period or appropriate punctuation."
    )
    context_block = "\n\n---\n".join(
        [
            f"[{i}] {c['title']} (chunk: {c['chunk_id']}):\n{c['text']}"
            for i, c in enumerate(contexts)
        ]
    )
    final_prompt = (
        f"{system_prompt}\n\nCONTEXTS:\n{context_block}\n\n"
        f"User question: {prompt}\n\n"
        "Answer with concise bullet points and include citations like [title:chunk_id]."
    )

    model = os.environ.get("VERTEX_TEXT_MODEL", "")
    project = os.environ.get("VERTEX_PROJECT", "")
    location = os.environ.get("VERTEX_LOCATION", "us-central1")

    if not model:
        raise RuntimeError("VERTEX_TEXT_MODEL environment variable not set")

    return call_vertex_text_generation(
        project=project,
        location=location,
        model=model,
        prompt=final_prompt,
    )


@app.post("/query")
async def query_endpoint(q: Dict = Body(...)):  # Made async
    user_query = q.get("query")
    top_k = q.get("top_k", 5)
    alpha = q.get("alpha", 0.5)

    if not user_query:
        raise HTTPException(status_code=400, detail="Query is required")

    # 1) hybrid retrieve
    hits = hybrid_search(user_query, top_k=top_k, alpha=alpha)
    # 2) call generator
    answer = call_vertex_rag(user_query, hits)
    return {"answer": answer, "sources": hits}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...), title: Optional[str] = None):
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Note: This is a temporary storage solution for testing.
    # Files will be lost when the container restarts.
    # For production, use a persistent storage solution like Google Cloud Storage.
    upload_dir = "/tmp/uploads"  # Use /tmp for Cloud Run
    os.makedirs(upload_dir, exist_ok=True)

    file_id = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, file_id)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        index_document(
            file_path=file_path,
            title=title or file.filename,
            metadata={"source": "upload", "original_filename": file.filename},
        )
        # Clean up the file after indexing
        os.remove(file_path)
    except ValueError as exc:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"status": "success", "file": file.filename}


@app.get("/healthz")
def health_check():
    checks = run_readiness_checks()
    status = "ok" if all(len(v) == 0 for v in checks.values()) else "degraded"
    return {"status": status, "checks": checks}


@app.get("/readyz")
def readiness_check():
    ready = is_system_ready()
    checks = run_readiness_checks()
    return {"ready": ready, "checks": checks}