"""Readiness checks for external dependencies."""

from __future__ import annotations

import os
from typing import Dict, List

from dotenv import load_dotenv, find_dotenv
from elasticsearch import Elasticsearch

from .vertex import get_access_token


load_dotenv(find_dotenv(), override=False)


REQUIRED_ENV_VARS = [
    "ELASTIC_URL",
    "VERTEX_PROJECT",
    "VERTEX_LOCATION",
    "VERTEX_EMBEDDING_MODEL",
    "VERTEX_TEXT_MODEL",
    "GOOGLE_APPLICATION_CREDENTIALS",
]


def _check_env() -> List[str]:
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    errors = []
    if missing:
        errors.append(f"Missing environment variables: {', '.join(missing)}")

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and not os.path.exists(creds_path):
        errors.append(f"Credentials file not found at {creds_path}")
    return errors


def _check_elastic() -> List[str]:
    elastic_url = os.environ.get("ELASTIC_URL")
    api_key = os.environ.get("ELASTIC_API_KEY")
    username = os.environ.get("ELASTIC_USER")
    password = os.environ.get("ELASTIC_PASS")

    if not elastic_url:
        return ["ELASTIC_URL is not configured"]

    try:
        if api_key:
            client = Elasticsearch(elastic_url, api_key=api_key)
        else:
            client = Elasticsearch(elastic_url, basic_auth=(username or "", password or ""))

        if not client.ping():
            return ["Unable to ping Elastic cluster"]
    except Exception as exc:  # pragma: no cover - network
        return [f"Elastic connectivity error: {exc}"]

    return []


def _check_vertex() -> List[str]:
    try:
        token = get_access_token()
        if not token:
            return ["Failed to obtain Vertex access token"]
    except Exception as exc:  # pragma: no cover - network
        return [f"Vertex credential error: {exc}"]
    return []


def run_readiness_checks() -> Dict[str, List[str]]:
    """Run readiness checks and return a dict with errors per subsystem."""
    results = {
        "environment": _check_env(),
        "elastic": _check_elastic(),
        "vertex": _check_vertex(),
    }
    return results


def is_system_ready() -> bool:
    """Convenience wrapper to return True when all checks pass."""
    results = run_readiness_checks()
    return all(len(messages) == 0 for messages in results.values())

