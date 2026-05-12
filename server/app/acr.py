import os
import hmac
import hashlib
import base64
import time
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

_HOST = os.environ["ACR_HOST"]
_KEY = os.environ["ACR_ACCESS_KEY"]
_SECRET = os.environ["ACR_ACCESS_SECRET"]
_ENDPOINT = f"https://{_HOST}/v1/identify"

def _sign(string_to_sign: str) -> str:
    secret = bytes(_SECRET, "utf-8")
    sig = hmac.new(secret, string_to_sign.encode("utf-8"), digestmod=hashlib.sha1)
    return base64.b64encode(sig.digest()).decode("utf-8")

async def identify(audio_bytes: bytes) -> dict | None:
    """
    Sends raw audio bytes to ACRCloud.
    Returns {title, artist} or None if not recognized.
    """
    timestamp = str(int(time.time()))
    string_to_sign = "\n".join(["POST", "/v1/identify", _KEY, "audio", "1", timestamp])
    signature = _sign(string_to_sign)

    data = {
        "access_key": _KEY,
        "sample_bytes": str(len(audio_bytes)),
        "timestamp": timestamp,
        "signature": signature,
        "data_type": "audio",
        "signature_version": "1",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            _ENDPOINT,
            data=data,
            files={"sample": ("sample.wav", audio_bytes, "audio/wav")},
        )

    body = response.json()

    # ACRCloud returns status code 0 on success
    if body.get("status", {}).get("code") != 0:
        return None

    metadata = body.get("metadata", {})
    music_list = metadata.get("music", [])
    if not music_list:
        return None

    music = music_list[0]

    return {
        "title": music["title"],
        "artist": music["artists"][0]["name"],
        "raw_acr": body,
    }