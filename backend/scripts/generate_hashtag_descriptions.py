from utils.hashatag_description import generate_hashtag_description
from utils.handle_json import load_json, save_json

from tqdm.auto import tqdm
from pathlib import Path
import time

####
# To run this script: `PYTHONPATH=./backend python backend/scripts/generate_hashtag_descriptions.py`
####

def generate_all_descriptions(tag_list):
    desc_by_tag = {}
    for tag in tqdm(tag_list, desc="Generating hashtag descriptions"):
        desc = generate_hashtag_description(tag)
        if desc:
            desc_by_tag[tag] = desc
        time.sleep(0.5)  # Rate limit handling
    return desc_by_tag

if __name__ == "__main__":
    backend_dir_path = Path(__file__).resolve().parent.parent
    data_dir_path = backend_dir_path.parent.parent / "data_cache"
    
    papers_path = data_dir_path / "machine_learning_100_v3.json"
    saving_path = data_dir_path / "machine_learning_100_v3_tag_desc.json"
    
    papers = load_json(papers_path)
    all_tags = []
    
    for paper in papers:
        all_tags.extend(paper["hashtags"])
    
    all_tags = list(set(all_tags))

    desc_by_tag = generate_all_descriptions(all_tags)

    save_json(data=desc_by_tag, file_path=saving_path)