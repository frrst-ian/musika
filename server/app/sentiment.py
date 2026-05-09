import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

_analyzer = SentimentIntensityAnalyzer()
_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))

# Maps compound score + dominant word patterns to a human emotion label
_EMOTION_MAP = [
    (0.5,  ["love", "happy", "joy", "wonderful", "beautiful", "amazing"], "joyful"),
    (0.3,  ["dance", "party", "energy", "run", "move", "beat"],           "energetic"),
    (0.05, [],                                                              "positive"),
    (-0.05,["alone", "empty", "lost", "gone", "miss", "cry", "tear"],     "melancholic"),
    (-0.3, ["hate", "anger", "rage", "fight", "war", "pain"],             "angry"),
    (-0.5, [],                                                              "negative"),
]

def _emotion(compound: float, tokens: list[str]) -> str:
    token_set = set(tokens)
    for threshold, keywords, label in _EMOTION_MAP:
        if compound >= threshold:
            if not keywords or token_set & set(keywords):
                return label
    return "negative"

def analyze(lyrics: str) -> dict:
    scores = _analyzer.polarity_scores(lyrics)
    compound = scores["compound"]

    tokens = word_tokenize(lyrics.lower())
    filtered = [_lemmatizer.lemmatize(w) for w in tokens
                if w.isalpha() and w not in _stop_words]

    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "emotion": _emotion(compound, filtered),
        "compound": round(compound, 4),
        "scores": {k: round(v, 4) for k, v in scores.items()},
        "top_words": filtered[:20],
    }