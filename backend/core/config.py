from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    app_name: str = "PaperHive API"
    environment: str = "development"
    
    # Elasticsearch settings
    es_hosts: List[str] = ["http://localhost:9200"]
    es_paper_index: str = "papers"       # alias name
    es_hashtag_index: str = "hashtags"   # alias name
    es_hashtag_relations_index: str = "hashtag_relations" #alias name
    
    hashtag_emb_dim: int = 256
    default_graph_steps: int = 2
    default_graph_top_n: int = 20

    openai_api_key: str = ""
 
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

settings = Settings()