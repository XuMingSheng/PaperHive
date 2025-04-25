import json
import openai

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def get_embedding(text, model="text-embedding-3-small"):
    openai.api_key = OPENAI_API_KEY
    return openai.embeddings.create(input=text, model=model, dimensions=256)

# Load input file
file_path = "hashtag_description.json"
with open(file_path, "r") as f:
    hashtag_description = json.load(f)

unique_hashtags = list(hashtag_description.keys())

# Generate embeddings
embeddings = get_embedding(unique_hashtags)

hashtag_embeddings = {}
for i, hashtag in enumerate(unique_hashtags):
    hashtag_embeddings[hashtag] = embeddings.data[i].embedding
    
print(len(embeddings.data))
print(len(unique_hashtags))

# Save to JSON
with open("hashtag_embeddings.json", "w") as f:
    json.dump(hashtag_embeddings, f)