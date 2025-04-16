import json
import openai

def get_embedding(text, model="text-embedding-3-small"):
    openai.api_key = "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"  # Or use environment variable
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