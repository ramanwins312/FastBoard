import os, json, httpx
from typing import AsyncIterator
from dotenv import load_dotenv
load_dotenv()

OR_URL = "https://openrouter.ai/api/v1/chat/completions"

def _headers():
    return {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "https://faster-notebook.vercel.app",
        "X-Title": "FasterNotebook",
        "Content-Type": "application/json",
    }
ROUTE = {
    "summary":    "openrouter/free",
    "flashcards": "openrouter/free",
    "quiz":       "openrouter/free",
    "mindmap":    "openrouter/free",
    "podcast":    "openrouter/free",
}

HUGE_MODEL = "openrouter/free"

FALLBACKS = [
    "openrouter/free"
]
async def stream_chat(task: str, system: str, user: str, big: bool = False) -> AsyncIterator:
    primary = HUGE_MODEL if big else ROUTE.get(task, ROUTE["summary"])
    for model in [primary] + FALLBACKS:
        payload = {
            "model": model,
            "stream": True,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                async with client.stream("POST", OR_URL, headers=_headers(), json=payload) as r:
                    if r.status_code != 200:
                        continue
                    async for line in r.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data = line[6:]
                        if data.strip() == "[DONE]":
                            return
                        try:
                            delta = json.loads(data)["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
                    return
        except Exception:
            continue
    yield "\n\n[Error: all free models are rate-limited right now. Wait 60s and retry.]"