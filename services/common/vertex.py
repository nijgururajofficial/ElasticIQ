"""Utility helpers for Vertex AI authentication and API calls."""

from __future__ import annotations
import json
import os
from typing import List
import google.auth
import google.auth.transport.requests
from google.auth import default
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def get_google_credentials(scopes=None):
    """
    Retrieve Google Cloud credentials.
    Tries service account first, falls back to application default credentials.
    """
    try:
        # Try to load service account credentials first
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            return service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=scopes or ['https://www.googleapis.com/auth/cloud-platform']
            )
    except Exception as e:
        print(f"Warning: Failed to load service account credentials: {e}")
    
    # Fall back to application default credentials
    credentials, _ = default(scopes=scopes)
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials

def get_access_token(scopes=None):
    """
    Get an access token from the default credentials.
    """
    credentials = get_google_credentials(scopes)
    credentials.refresh(Request())
    return credentials.token

def call_vertex_embeddings(project: str, location: str, model: str, texts: List[str]) -> List[List[float]]:
    """Call Vertex AI Embedding model (text-embedding-004)."""
    endpoint = (
        f"https://{location}-aiplatform.googleapis.com/v1"
        f"/projects/{project}/locations/{location}/publishers/google/models/{model}:predict"
    )

    payload = {"instances": [{"content": t} for t in texts]}
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }

    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    if not response.ok:
        raise RuntimeError(
            f"Vertex AI Embedding call failed: {response.status_code}, {response.text}"
        )

    data = response.json()
    embeddings: List[List[float]] = []
    for prediction in data.get("predictions", []):
        if not isinstance(prediction, dict):
            continue

        if "embedding" in prediction and isinstance(prediction["embedding"], dict):
            values = prediction["embedding"].get("values")
            if values is not None:
                embeddings.append(values)
                continue

        if "embeddings" in prediction:
            embedded = prediction["embeddings"]
            if isinstance(embedded, dict) and "values" in embedded:
                embeddings.append(embedded["values"])
                continue
            if isinstance(embedded, list) and embedded:
                first = embedded[0]
                if isinstance(first, dict) and "values" in first:
                    embeddings.append(first["values"])
                    continue

        if "values" in prediction:
            embeddings.append(prediction["values"])

    if not embeddings:
        raise RuntimeError(
            "Vertex AI Embedding call returned unexpected payload",
        )

    return embeddings

def call_vertex_text_generation(
    project: str,
    location: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    max_output_tokens: int = 2048,  # Increased token limit
    top_k: int = 40,
    top_p: float = 0.8,
) -> str:
    """Call Vertex AI text generation model (Gemini)."""
    endpoint = (
        f"https://{location}-aiplatform.googleapis.com/v1"
        f"/projects/{project}/locations/{location}/publishers/google/models/{model}:generateContent"
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
            "topK": top_k,
            "topP": top_p,
            "stopSequences": ["</answer>"]
        }
    }

    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }

    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    if not response.ok:
        error_msg = f"Vertex AI Text Gen call failed: {response.status_code}"
        try:
            error_details = response.json()
            if isinstance(error_details, dict):
                error_msg += f", {error_details.get('error', {}).get('message', '')}"
        except:
            error_msg += f", {response.text[:200]}"
        raise RuntimeError(
            error_msg
        )

    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return "No response generated. Please try rephrasing your question."

    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [p.get("text", "") for p in parts]
    full_response = "".join(texts).strip()
    
    # Remove any truncated sentences at the end
    if full_response and not any(full_response.endswith(p) for p in ['.', '!', '?', ':', ';']):
        last_sentence = full_response.split('.')[-1]
        full_response = full_response[:-(len(last_sentence))]
    
    return full_response or "Response was empty. Please try again."