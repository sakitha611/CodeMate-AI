
import os
from openai import OpenAI

SYSTEM = """You are BUGZERO AI, a careful senior software engineer.
Analyze only the code and task supplied. Never claim code was executed or tested unless a tool actually ran it.
Return clear, actionable advice. When asked for JSON, return valid JSON only."""

def ask_ai(task, code="", language="unknown"):
    api_key = os.getenv("NVIDIA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not configured. Add it to your .env file."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv(
            "NVIDIA_BASE_URL",
            "https://integrate.api.nvidia.com/v1"
        )
    )

    response = client.chat.completions.create(
        model=os.getenv(
            "NVIDIA_MODEL",
            "meta/llama-3.3-70b-instruct"
        ),
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": f"Task: {task}\nLanguage: {language}\nCode/context:\n{code}"
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content or ""
