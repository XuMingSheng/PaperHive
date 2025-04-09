paper_index_mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "abstract": {"type": "text"},
            "authors": {"type": "keyword"},
            "arxiv_id": {"type": "keyword"},
            "doi": {"type": "keyword"},
            "year": {"type": "integer"},
            "hashtags": {"type": "keyword"},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    }
}