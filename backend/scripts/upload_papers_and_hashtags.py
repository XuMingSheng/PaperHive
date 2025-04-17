from utils.handle_json import load_json

import requests
from pathlib import Path
from tqdm.auto import tqdm

####
# To run this script at the project root: `$PYTHONPATH=./backend python backend/scripts/upload_papers_and_hashtags.py`
####

API_BASE = "http://localhost:8000/api/v1"

HEADERS = {
    "Content-Type": "application/json"
}

def create_hashtag(hashtag):
    res = requests.post(
        f"{API_BASE}/hashtags/",
        headers=HEADERS,
        json=hashtag
    )
    if res.status_code not in [200, 201, 409]:
        print(f"Failed to create hashtag: {hashtag.get('name')} | Status: {res.status_code}")


def create_paper(paper):
    res = requests.post(
        f"{API_BASE}/papers/",
        headers=HEADERS,
        json=paper
    )
    if res.status_code not in [200, 201, 409]:
        print(f"Failed to create paper: {paper.get('title')} | Status: {res.status_code}")


def main():
    backend_dir_path = Path(__file__).resolve().parent.parent
    data_dir_path = backend_dir_path.parent.parent / "data_cache"

    papers_path = data_dir_path / "quantum_500.json"
    tag_desc_path = data_dir_path / "quantum_500_tag_desc.json"
    tag_embs_path = data_dir_path / "quantum_500_tag_embs.json"

    papers = load_json(papers_path)
    tag_embs = load_json(tag_embs_path)
    tag_desc = load_json(tag_desc_path)

    # hashtag_cnt = {} 
    # for paper in papers:
    #     hashtags = [tag.strip() for tag in paper["hashtags"].split(",")]
    #     paper["hashtags"] = hashtags
        
    #     for tag in hashtags:
    #         hashtag_cnt[tag] = hashtag_cnt.get(tag, 0) + 1

    # selected_hashtags = set([tag for tag, cnt in hashtag_cnt.items() if cnt > 1]) 
    # selected_hashtags = set([tag for tag, cnt in hashtag_cnt.items()])
    selected_hashtags = set(tag_embs.keys())

    print(f"selected tags cnt: {len(selected_hashtags)}")
    print(f"tag with desc cnt: {len(tag_desc)}")
    print(f"tag witg embs cnt: {len(tag_embs)}")

    hashtags = []
    for name in selected_hashtags:
        hashtag = {
            "name": name,
            "description": tag_desc[name],
            "embedding": tag_embs[name]
        }
        hashtags.append(hashtag)

    for paper in papers:
        paper["hashtags"] = [tag for tag in paper["hashtags"] if tag in selected_hashtags]

    # Create hashtags first
    print("Uploading hashtags...")
    for hashtag in tqdm(hashtags):
        create_hashtag(hashtag)

    # Create papers
    print("\nUploading papers...")
    for paper in tqdm(papers):
        create_paper(paper)


if __name__ == "__main__":
    main()