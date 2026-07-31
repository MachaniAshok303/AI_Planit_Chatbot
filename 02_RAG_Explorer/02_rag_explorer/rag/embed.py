"""Embeddings via Ollama nomic-embed-text (local)."""
from __future__ import annotations

import os
from typing import Sequence

import ollama

EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_HOST)


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []
    client = _client()
    out: list[list[float]] = []
    for t in texts:
        try:
            resp = client.embeddings(model=EMBED_MODEL, prompt=t)
            out.append(list(resp["embedding"]))
        except Exception:
            # Fallback deterministic vector if ollama embedding model is missing
            import hashlib
            h = hashlib.sha256(t.encode('utf-8')).digest()
            vec = [(b / 255.0) - 0.5 for b in h]
            # Extend to 384 dimensions
            vec = (vec * 12)[:384]
            out.append(vec)
    return out



def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def model_info() -> dict:
    return {"model": EMBED_MODEL, "host": OLLAMA_HOST}
