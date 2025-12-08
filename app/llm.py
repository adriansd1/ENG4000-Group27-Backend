import re
import requests
from typing import Optional
import logging
import time

from .config import settings

logger = logging.getLogger(__name__)

def call_ollama(prompt: str) -> str:
    """
    Sends a single user prompt to the local Ollama model, logs latency
    and returns the model's response text. All other modules should call
    the LLM through this function only.
    """
    url = f"{settings.OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
    }
    start_time = time.time()

    try:
        response = requests.post(url, json=payload, timeout=800)
        response.raise_for_status()
    except Exception as e:
        logger.error(
            f"LLM call failed for model={settings.OLLAMA_MODEL}: {e}"
        )
        raise

    latency = time.time() - start_time  # --- NEW: compute latency ---

    # NEW: logging the performance:
    logger.info(
        f"LLM call success | model={settings.OLLAMA_MODEL} | latency={latency:.2f} sec | prompt_chars={len(prompt)}",
    )

    data = response.json()
    # return data["message"]["content"]

    # response = requests.post(url, json=payload, timeout=800)
    # response.raise_for_status()
    # data = response.json()
    # return data["message"]["content"]

    # Defensive Parsing in case the response format changes
    message = data.get("message", {})
    content = message.get("content", "")

    if not content:
        logger.error("LLM response has no 'message.content': %s", data)
        raise ValueError("LLM returned an empty or malformed response.")

    return content


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
