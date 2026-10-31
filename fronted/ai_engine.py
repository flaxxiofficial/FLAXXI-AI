import os
import requests

AI_URL = os.getenv("OLLAMA_URL","http://localhost:11434")

MODEL = os.getenv("AI_MODEL","qwen2.5:3b")

SYSTEM_PROMPT = """
You are FLAXXI AI.

You are a general purpose intelligent AI assistant.

You can answer questions, reason, explain,
generate and debug programming code.

Supported languages:

HTML, CSS, JavaScript, Python, Java,
Kotlin, C, C++, JSON, XML, PHP,
SQL, TypeScript, Dart and Smali.

Generate complete source code when requested.

Explain errors and provide corrected code.

Never claim an action was completed unless it actually was.
"""


def ask_ai(message,history=None):

    messages = [
        {"role":"system","content":SYSTEM_PROMPT}
    ]

    if history:
        messages.extend(history[-20:])

    messages.append({
        "role":"user",
        "content":message
    })

    response = requests.post(
        AI_URL.rstrip("/") + "/api/chat",
        json={
            "model":MODEL,
            "messages":messages,
            "stream":False
        },
        timeout=300
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def generate_code(prompt,language):

    return ask_ai(
        f"Generate complete {language} code.\n\n{prompt}"
    )
