from services import PaperService, HashtagService, PdfService
from db.elastic import get_elasticsearch

def get_paper_service() -> PaperService:
    es = get_elasticsearch()
    return PaperService(es)

def get_hashtag_service() -> HashtagService:
    es = get_elasticsearch()
    return HashtagService(es)

def get_pdf_service() -> PdfService:
    es = get_elasticsearch()
    return PdfService(es)
