import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

SUMMARY_SYSTEM_PROMPT = (
    "You are a senior software engineer reviewing code for documentation purposes. "
    "For the given file, respond with a concise summary covering: "
    "1) Purpose of this file, 2) Key functions/classes/exports, "
    "3) Notable dependencies or imports. "
    "Keep it to 3-5 sentences. Do not repeat the raw code. Be factual, not speculative."
)


def summarize_file(relative_path: str, content: str) -> str:
    if not content.strip():
        return "Empty file."

    user_prompt = f"File: {relative_path}\n\n```\n{content}\n```"

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=250,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()