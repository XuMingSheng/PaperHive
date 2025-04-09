import random

def mock_embedding(text: str, dim: int = 768) -> list[float]:
    return [random.uniform(-1, 1) for _ in range(dim)]