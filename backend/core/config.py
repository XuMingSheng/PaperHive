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
    
    hashtag_emb_dim: int = 256
 
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

settings = Settings()