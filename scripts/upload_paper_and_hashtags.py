import json
import requests
from tqdm.auto import tqdm

API_BASE = "http://localhost:8000/api/v1"

HEADERS = {
    "Content-Type": "application/json"
}

def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_hashtag(tag_name, emb):
    res = requests.post(
        f"{API_BASE}/hashtags/",
        headers=HEADERS,
        json={
            "name": tag_name,
            "embedding": emb
        }
    )
    if res.status_code not in [200, 201, 409]:
        print(f"Failed to create hashtag: {tag_name} | Status: {res.status_code}")
    # else:
    #     print(f"Created hashtag: {tag_name}")


def create_paper(paper):
    res = requests.post(
        f"{API_BASE}/papers/",
        headers=HEADERS,
        json=paper
    )
    if res.status_code not in [200, 201, 409]:
        print(f"Failed to create paper: {paper.get('title')} | Status: {res.status_code}")
    # else:
    #     print(f"Created paper: {paper.get('title')}")


def main():
    data = load_data("../machine_learning_100_v3.json")
    embeddings = load_data("../hashtag_embeddings.json")
    print(len(embeddings))

    hashtag_cnt = {} 
    for item in data:
        hashtags = [tag.strip().lower() for tag in item["hashtags"].split(",")]
        for tag in hashtags:
            hashtag_cnt[tag] = hashtag_cnt.get(tag, 0) + 1

    # selected_hashtags = set([tag for tag, cnt in hashtag_cnt.items() if cnt > 1]) 
    selected_hashtags = set([tag for tag, cnt in hashtag_cnt.items()])


    papers = []

    for item in data:
        hashtags = [tag.strip().lower() for tag in item["hashtags"].split(",")]

        paper = {
            "arxiv_id": item["arxiv_id"],
            "doi": item["doi"],
            "title": item["title"],
            "abstract": item["abstract"],
            "year": item["year"],
            "authors": item["authors"],
            "hashtags": [tag for tag in hashtags if tag in selected_hashtags]
        }

        papers.append(paper)

    # Create hashtags first
    print("Uploading hashtags...")
    for tag in tqdm(selected_hashtags):
        create_hashtag(tag_name=tag, emb=embeddings[tag])

    # Create papers
    print("\nUploading papers...")
    for paper in tqdm(papers):
        create_paper(paper)


if __name__ == "__main__":
    main()