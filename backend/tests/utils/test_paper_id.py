from utils.paper_id import generate_paper_id

def test_doi_preference():
    assert generate_paper_id(arxiv_id="1234.5678", doi="10.1000/xyz").startswith("doi:")

def test_arxiv_fallback():
    assert generate_paper_id(arxiv_id="1234.5678").startswith("arxiv:")

def test_uuid_fallback():
    id = generate_paper_id()
    assert len(id) == 36  # UUID4 length