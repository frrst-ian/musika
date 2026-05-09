import re
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

_nlp = spacy.load("en_core_web_sm")
_stop_words = set(stopwords.words("english")) - {"by", "the"}

_FILLER = re.compile(
    r"\b(play|search|find|song|music|track|called|titled|singer|artist|band)\b",
    re.IGNORECASE,
)

def parse_transcript(transcript: str) -> dict:
    """
    Accepts raw STT transcript 
    Returns {title, artist} best-effort parsed.
    """
    cleaned = _FILLER.sub("", transcript).strip()

    # Primary: split on 'by'
    by_split = re.split(r"\bby\b", cleaned, maxsplit=1, flags=re.IGNORECASE)
    if len(by_split) == 2:
        return {
            "title": by_split[0].strip(),
            "artist": by_split[1].strip(),
            "raw": transcript,
        }

    # Fallback: spaCy NER — PERSON or ORG entities are likely the artist
    doc = _nlp(cleaned)
    entities = [(ent.text, ent.label_) for ent in doc.ents
                if ent.label_ in ("PERSON", "ORG", "GPE")]

    if entities:
        artist = entities[0][0]
        title = cleaned.replace(artist, "").strip(" -,")
        return {"title": title, "artist": artist, "raw": transcript}

    # Last resort: first half / second half split
    words = word_tokenize(cleaned)
    mid = len(words) // 2
    return {
        "title": " ".join(words[:mid]),
        "artist": " ".join(words[mid:]),
        "raw": transcript,
    }