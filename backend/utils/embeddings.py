from core.config import settings
import random
from typing import List

def mock_embedding(tag: str, dim: int = settings.hashtag_emb_dim) -> list[float]:
    return [random.uniform(-1, 1) for _ in range(dim)]


def generate_hashtag_embeddings(tag: str, dim: int = settings.hashtag_emb_dim) -> list[float]:
    return mock_embedding(tag, dim)


def average_embeddings(embeddings: List[List[float]]) -> List[float]:
    if not embeddings:
        return []

    dim = len(embeddings[0])
    pooled = [0.0] * dim

    for emb in embeddings:
        for i in range(dim):
            pooled[i] += emb[i]

    return [x / len(embeddings) for x in pooled]