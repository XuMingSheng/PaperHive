from uuid import uuid4
from typing import Optional

def generate_paper_id(arxiv_id: Optional[str] = None, doi: Optional[str] = None) -> str:
    if doi:
        return f"doi:{doi.lower().strip()}"
    elif arxiv_id:
        return f"arxiv:{arxiv_id.lower().strip()}"
    
    return str(uuid4())