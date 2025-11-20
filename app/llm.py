import re
import requests
from typing import Optional

from .config import settings


def call_ollama(prompt: str) -> str:
    """
    Call local Ollama chat API with a single user message and return the content.
    """
    url = f"{settings.OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
    }
    response = requests.post(url, json=payload, timeout=800)
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


def extract_sql_from_text(text: str) -> str:
    """
    Extract SQL from ```sql fenced block OR any ``` fenced block.
    Cleans up weird spacing or invisible characters.
    """

    import re

    # 1. Try strict ```sql ... ```
    strict = re.search(r"```sql\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if strict:
        return strict.group(1).strip()

    # 2. Try generic ```...```
    generic = re.search(r"```\s*(.*?)\s*```", text, flags=re.DOTALL)
    if generic:
        return generic.group(1).strip()

    # 3. Try lines that start with SELECT
    for line in text.splitlines():
        if line.strip().lower().startswith("select"):
            return line.strip()

    # 4. Fallback → return everything (still cleaned)
    return text.strip()
