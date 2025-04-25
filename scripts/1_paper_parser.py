import arxiv
import requests
import os
import json
from typing import List
import openai

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def generate_hashtags(abstract):

    openai.api_key = OPENAI_API_KEY
    prompt = '''
    Given the following abstract, give me 10 terms of topics or classification or keywords.
     7 of terms should be common, broad, general in papers and 3 are more specific to abstract,
     please output only one line.
     term should be no more than three words, 
     start with uppercase letters,
      be separated by commas, and contain no other text, and no any symbol characters.
      No need to exist in abstract
    '''
    prompt += abstract
    response = openai.responses.create(
        model="gpt-4o-mini",
        input = prompt
    )
    return response.output_text


counter = 0
pdf_dir = "papers"
os.makedirs(pdf_dir, exist_ok=True)
client = arxiv.Client()
all_papers = []
unique_paper_ids = set()

# total result = len(keywords) * max_results
max_results_per_keyword = 50 # number of papers per keyword
keywords = [
    "quantum machine learning", "quantum computing", "quantum cryptography", "quantum algorithms", "quantum information theory",
    "quantum error correction", "quantum simulation", "quantum physics", "quantum materials", "quantum field theory "
]
for keyword in keywords:
    search = arxiv.Search(
        query=keyword,
        max_results=max_results_per_keyword * 4,
        sort_by=arxiv.SortCriterion.Relevance
    )
    category_counter = 0
    for result in client.results(search):
        if category_counter == max_results_per_keyword:
            break
        arxiv_id = result.get_short_id()
        if arxiv_id in unique_paper_ids:
            continue
        unique_paper_ids.add(arxiv_id)
        
        title = result.title.strip().replace("\n", " ")
        abstract = result.summary.strip().replace("\n", " ")
        year = result.published.year
        authors = [author.name for author in result.authors]
        doi = result.doi if result.doi else ""
        hashtags = []
        counter += 1
        category_counter += 1
        print(f"{counter}-{keyword}: {title}")

        # save metadata
        all_papers.append({
            "arxiv_id": arxiv_id,
            "doi": doi,
            "title": title,
            "abstract": abstract,
            "year": year,
            "authors": authors,
            "hashtags": hashtags
        })

for paper in all_papers:
    abstract = paper["abstract"]
    hashtags_raw = generate_hashtags(abstract)
    paper["hashtags"] = [tag.strip() for tag in hashtags_raw.split(',') if tag.strip()]

saved_file_path = "quantum_500.json"
with open(saved_file_path, "w", encoding="utf-8") as f:
    json.dump(all_papers, f, indent=2, ensure_ascii=False)

print("Finished ：save metadata to ", saved_file_path)