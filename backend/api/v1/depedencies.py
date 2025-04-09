from services import PaperService, HashtagService
from db.elastic import get_elasticsearch

def get_paper_service() -> PaperService:
    es = get_elasticsearch()
    return PaperService(es)

def get_hashtag_service() -> HashtagService:
    es = get_elasticsearch()
    return HashtagService(es)

    
