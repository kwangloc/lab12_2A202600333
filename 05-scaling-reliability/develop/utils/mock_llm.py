"""
Mock LLM — dùng chung cho tất cả ví dụ.
Không cần API key thật. Trả lời giả lập để focus vào deployment concept.
"""
import time
import random


MOCK_RESPONSES = {
    "default": [
        "This is a mock response from the agent. Ask me anything!",
        "Agent is running smoothly! (mock response) Ask another question.",
        "I am an AI agent deployed on the cloud. Your question has been received.",
    ],
    "docker": ["Container is a way to package an app to run anywhere. Build once, run anywhere!"],
    "deploy": ["Deployment is the process of moving code from your machine to a server for others to use."],
    "health": ["Agent is running smoothly. All systems operational."],
}


def ask(question: str, delay: float = 0.1) -> str:
    """
    Mock LLM call với delay giả lập latency thật.
    """
    time.sleep(delay + random.uniform(0, 0.05))  # simulate API latency

    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)

    return random.choice(MOCK_RESPONSES["default"])


def ask_stream(question: str):
    """
    Mock streaming response — yield từng token.
    """
    response = ask(question)
    words = response.split()
    for word in words:
        time.sleep(0.05)
        yield word + " "
