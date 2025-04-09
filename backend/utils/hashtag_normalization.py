def normalize_hashtag(name: str) -> str:
    return name.strip().lstrip("#").lower()
