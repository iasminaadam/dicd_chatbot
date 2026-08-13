import os
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="DICD AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None


class Page(BaseModel):
    url: str
    title: str
    text: str


class ChatRequest(BaseModel):
    message: str
    page: Page
    history: list[dict[str, Any]] = []


SYSTEM_PROMPT = """You are the DICD TUIASI website assistant.

Your job is to help a visitor understand and navigate the DICD website.

Rules:
- Answer in Romanian unless the user writes in another language.
- Treat the CURRENT PAGE context as the user's present location on the site.
- Use the supplied page text as the primary source for questions about the current page.
- Do not invent DICD procedures, links, contact details, or capabilities.
- If the page text does not contain enough information, say so clearly.
- When useful, explain the next action as a short numbered sequence.
- Be concise and practical.
"""


@app.get("/health")
def health():
    return {
        "ok": True,
        "model_configured": bool(client),
        "model": MODEL
    }


@app.post("/api/chat")
def chat(req: ChatRequest):

    if not client:
        return {
            "answer": (
                "Backend-ul funcționează, dar GEMINI_API_KEY "
                "nu este configurat încă. "
                "Adaugă cheia Gemini în fișierul .env."
            )
        }

    history_text = "\n".join(
        f'{m.get("role", "unknown")}: {m.get("text", "")}'
        for m in req.history[-10:]
    )

    user_input = f"""CURRENT PAGE

URL: {req.page.url}
TITLE: {req.page.title}

PAGE TEXT

{req.page.text}

RECENT CONVERSATION

{history_text}

USER QUESTION

{req.message}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=800,
        ),
    )

    return {
        "answer": response.text
    }


if __name__ == "__main__":

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )