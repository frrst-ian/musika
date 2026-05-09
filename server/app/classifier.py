import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ["GROQ_TOKEN"])
GENRE_LABELS = ["pop", "hip-hop", "rock", "r&b", "electronic", "country", "jazz", "classical"]

def classify_genre(lyrics: str) -> dict:
    prompt = f"""You are a music genre classifier.

Given these song lyrics, classify the genre and return ONLY a JSON object with no markdown, no explanation.

Lyrics:
{lyrics[:2000]}

Return this exact format:
{{
  "genre": "the top genre from this list: {GENRE_LABELS}",
  "confidence": <float 0-100>,
  "all_scores": {{"pop": <float>, "hip-hop": <float>, "rock": <float>, "r&b": <float>, "electronic": <float>, "country": <float>, "jazz": <float>, "classical": <float>}}
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )

    text = response.choices[0].message.content.strip()
    return json.loads(text)