hashtag_relations_index_mapping = {
    "mappings": {
         "properties": {
            # "id": src_dst
            "src": {"type": "keyword"},
            "dst": {"type": "keyword"},
            "paper_cnt_total": {"type": "integer"},
            "paper_cnt_by_year": {"type": "object"}
        }   
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    }
}