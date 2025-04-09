hashtag_index_mapping = {
    "mappings": {
         "properties": {
            "name": {"type": "text"},
            "description": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            }
        }   
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    }
}