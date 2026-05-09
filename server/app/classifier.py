import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
GENRE_LABELS = ["pop", "hip-hop", "rock", "r&b", "electronic", "country", "jazz", "classical"]

headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}

def classify_genre(lyrics: str) -> dict:
    payload = {
        "inputs": lyrics[:1500],
        "parameters": {"candidate_labels": GENRE_LABELS},
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    top = result[0]
    return {
        "genre": top["label"],
        "confidence": round(top["score"] * 100, 2),
        "all_scores": {item["label"]: round(item["score"] * 100, 2) for item in result},
    }

if __name__ == "__main__":
    sample = "Nowadays everybody wanna talk like they got something to say but nothing comes out when they move their lips just a bunch of gibberish"
    print(classify_genre(sample))