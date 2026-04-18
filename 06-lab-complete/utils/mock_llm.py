"""
Gemini LLM — Google Gemini 2.0 Flash via google-genai SDK.
Requires GEMINI_API_KEY environment variable.
Falls back to mock responses if API key is not set.
"""
import os
import time
import random
import logging

logger = logging.getLogger(__name__)

_GEMINI_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Lazy-init client — only import/connect when actually needed
_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=_API_KEY)
    return _client


# Fallback mock (used when GEMINI_API_KEY is not set)
_MOCK_RESPONSES = [
    "Đây là câu trả lời từ AI agent (mock — set GEMINI_API_KEY to use real Gemini).",
    "Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.",
    "Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.",
]


def ask(question: str, delay: float = 0.0) -> str:
    """
    Call Gemini API. Falls back to mock if GEMINI_API_KEY is not set.
    """
    if not _API_KEY:
        logger.warning("GEMINI_API_KEY not set — using mock response")
        time.sleep(delay + random.uniform(0, 0.05))
        return random.choice(_MOCK_RESPONSES)

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=question,
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e} — falling back to mock response")
        return random.choice(_MOCK_RESPONSES)


def ask_stream(question: str):
    """
    Streaming response from Gemini. Falls back to mock if no API key.
    """
    if not _API_KEY:
        response = ask(question)
        for word in response.split():
            time.sleep(0.05)
            yield word + " "
        return

    try:
        client = _get_client()
        for chunk in client.models.generate_content_stream(
            model=_GEMINI_MODEL,
            contents=question,
        ):
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"Gemini stream error: {e}")
        raise
