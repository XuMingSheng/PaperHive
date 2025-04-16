import json
from collections import Counter

file_path =  "quantum_500.json"

all_papers = []
all_hashtags = []
all_id = []

# 讀取 JSON 檔案
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 假設每筆資料都是一個 dict 並存在一個 list 裡面
for entry in data:
    arxiv_id = entry.get("arxiv_id", "")
    doi = entry.get("doi", "")
    title = entry.get("title", "")
    abstract = entry.get("abstract", "")
    year = entry.get("year", "")
    authors = entry.get("authors", [])
    hashtags = entry.get("hashtags", [])

    all_papers.append({
        "arxiv_id": arxiv_id,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "year": year,
        "authors": authors,
        "hashtags": hashtags
    })
    all_id.append(arxiv_id)
    all_hashtags.extend(hashtags)

print(len(Counter(all_hashtags)))
# 統計 hashtags 出現次數
hashtag_counts = Counter(all_hashtags)
top_hashtags = hashtag_counts.most_common(30)
for idx, (hashtag, count) in enumerate(top_hashtags, start=1):
    print(f"{idx:2d}. {hashtag}: {count}")

unique_hashtag_count = len(hashtag_counts)

valid_hashtags = {tag: count for tag, count in hashtag_counts.items() if count > 1}
valid_count = len(valid_hashtags)
print(f"After filrer, there are still {valid_count} independent hashtags")
# 可選：轉成排序後的 list of dict
# hashtag_counts_list = [
#     {"hashtag": k, "count": v}
#     for k, v in sorted(dict(hashtag_counts).items(), key=lambda item: item[1], reverse=True)
# ]
# print(hashtag_counts)

# 再重新處理每筆資料，過濾 hashtags
all_papers = []
for entry in data:
    arxiv_id = entry.get("arxiv_id", "")
    doi = entry.get("doi", "")
    title = entry.get("title", "")
    abstract = entry.get("abstract", "")
    year = entry.get("year", "")
    authors = entry.get("authors", [])

    # 拆解並過濾 hashtags
    hashtags = entry.get("hashtags", "")
    filtered_hashtags = [tag for tag in hashtags if tag in valid_hashtags]
    print(f"Filtered hashtags: {filtered_hashtags}")
    all_papers.append({
        "arxiv_id": arxiv_id,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "year": year,
        "authors": authors,
        "hashtags": filtered_hashtags
    })

# # 可以把結果寫到檔案或繼續處理
with open("filtered_"+file_path, 'w', encoding='utf-8') as f:
    json.dump(all_papers, f, ensure_ascii=False, indent=2)