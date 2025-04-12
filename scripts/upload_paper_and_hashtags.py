import json
import requests

API_BASE = "http://localhost:8000/api/v1"

HEADERS = {
    "Content-Type": "application/json"
}

def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_hashtag(tag_name):
    res = requests.post(
        f"{API_BASE}/hashtags/",
        headers=HEADERS,
        json={"name": tag_name}
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
    data = load_data("../machine_learninig_500.json")

    hashtag_set = set()
    papers = []

    for item in data:
        hashtags = [tag.strip() for tag in item["hashtags"].split(",")]
        hashtag_set.update(hashtags)

        paper = {
            "arxiv_id": item["arxiv_id"],
            "doi": item["doi"],
            "title": item["title"],
            "abstract": item["abstract"],
            "year": item["year"],
            "authors": item["authors"],
            "hashtags": hashtags
        }

        papers.append(paper)

    # Create hashtags first
    print("Uploading hashtags...")
    for tag in sorted(hashtag_set):
        create_hashtag(tag)

    # Create papers
    print("\nUploading papers...")
    for paper in papers:
        create_paper(paper)


if __name__ == "__main__":
    main()