from core.config import settings
import openai

def placeholder_hashtag_description(tag: str):
    return f"<The description of {tag}>" 


def generate_hashtag_description(tag: str):
    client = openai.OpenAI(api_key=settings.openai_api_key)
    
    prompt = f"""
    Describe the following research terms in one short, informative sentence.

    Term: transfer learning
    Description: A technique where a model trained on one task is adapted for a different but related task.

    Term: graph neural networks
    Description: Neural networks that operate directly on graph-structured data using message passing.

    Term: {tag}
    Description:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )
        resp_text = response.choices[0].message.content.strip()
        return resp_text
    except Exception as e:
        print(f"Error generating for '{tag}': {e}")
        return None