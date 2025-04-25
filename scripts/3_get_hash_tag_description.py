import json
import openai
from collections import Counter

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def generate_hashtags_description(hashtag):

    openai.api_key = OPENAI_API_KEY
    prompt = '''
    Given this term, give me a short description of it. no more than a paragraph. The term is : 
    '''
    prompt += hashtag
    response = openai.responses.create(
        model="gpt-4o-mini",
        input = prompt
    )
    return response.output_text

# 讀取過濾後的資料
file_name = "filtered_quantum_500.json"
with open(file_name, 'r', encoding='utf-8') as f:
    papers = json.load(f)

# 收集所有 hashtags
all_hashtags = []
counter = 0
for paper in papers:
    hashtags = paper.get("hashtags", [])
    # print(hashtags)
    all_hashtags.extend(hashtags)
    counter += len(hashtags)


# 建立 unique hashtags set
unique_hashtags = set(all_hashtags)
print("There are ", len(unique_hashtags), " unique hashtags in the dataset.")
hashtag_description = {}
for tag in unique_hashtags:
    # 模擬一段文字分析結果
    hashtag_description[tag] = generate_hashtags_description(tag)
    print(tag, ":", hashtag_description[tag])

with open("hashtag_description.json", "w", encoding="utf-8") as f:
    json.dump(hashtag_description, f, indent=2, ensure_ascii=False)