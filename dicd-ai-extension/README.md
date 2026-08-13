# DICD AI Assistant — Chrome Extension MVP

This is the first working prototype of a page-aware AI assistant for
https://dicd.tuiasi.ro/

It does NOT require access to the DICD website source code.

## Architecture

Browser
  -> Chrome content script
  -> reads current page URL/title/main text
  -> sends question + page context to localhost:8000
  -> FastAPI backend
  -> OpenAI Responses API
  -> answer returned to extension

## 1. Start the backend

Requirements: Python 3.10+

From the `backend` directory:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and set:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-mini
```

Start:

```bash
python main.py
```

The API should be available at:

http://localhost:8000

Test:

http://localhost:8000/health

## 2. Load the extension in Chrome

Open:

`chrome://extensions`

Turn on **Developer mode**.

Choose **Load unpacked**.

Select the `extension` folder from this project.

Then open:

https://dicd.tuiasi.ro/ro/

You should see a floating ✦ button in the bottom-right corner.

## 3. Test it

Click the button and ask something such as:

- "Despre ce este această pagină?"
- "Care este următorul pas?"
- "Explică-mi pagina pe scurt."

The extension sends the current page context to the backend.

## Important security note

Never put an OpenAI API key in the extension JavaScript.

The extension calls your backend; only the backend holds the API key.

## Next development steps

1. Add DICD site-wide RAG/search.
2. Add clickable links to DICD pages.
3. Detect and highlight relevant buttons/links on the current page.
4. Add a "Guide me" mode.
5. Add conversation persistence.
6. Add a proper production backend and authentication/rate limiting.
7. Replace `allow_origins=["*"]` with the exact extension origin/backend policy for production.
