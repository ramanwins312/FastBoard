from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from uuid import uuid4
import time
import llm
import ingest 
import prompts 

app = FastAPI()

# --- THE CORS BOUNCER FIX ---
# (Leave the rest of your file exactly as it is below here)
# --- THE CORS BOUNCER FIX ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your Next.js app to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCS: dict[str, dict] = {}

@app.get("/")
def health():
    return {"ok": True, "docs": len(DOCS)}

@app.post("/ingest")
async def ingest_route(
    file: UploadFile | None = File(None),
    url: str | None = Form(None),
    text: str | None = Form(None),
):
    content, name = "", "untitled"
    try:
        if file:
            buf = await file.read()
            name = file.filename or "upload"
            if name.lower().endswith(".pdf"):
                content = ingest.from_pdf(buf)
            else:
                content = buf.decode("utf-8", errors="ignore")
        elif url:
            content = ingest.from_url(url); name = url
        elif text:
            content = text; name = "pasted-text"
        else:
            raise HTTPException(400, "Provide file, url, or text")
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(500, f"Ingest failed: {e}")

    if not content.strip():
        raise HTTPException(422, "Could not extract any text from this source.")

    content = content[:400_000]
    doc_id = str(uuid4())
    DOCS[doc_id] = {"text": content, "name": name, "ts": time.time()}
    return {"doc_id": doc_id, "name": name, "chars": len(content)}

VALID_TASKS = {"summary", "flashcards", "quiz", "mindmap", "podcast"}

@app.post("/generate")
async def generate(
    doc_id: str = Form(...),
    task: str = Form(...),
    emphasis: str = Form(""),
    n: int = Form(8),
):
    if task not in VALID_TASKS:
        raise HTTPException(400, f"task must be one of {VALID_TASKS}")
    doc = DOCS.get(doc_id)
    if not doc:
        raise HTTPException(404, "doc_id not found")

    big = len(doc["text"]) > 60_000
    tpl = getattr(prompts, task.upper())
    sys_msg = tpl.format(emphasis=emphasis or "none", n=n)
    user_msg = f"DOCUMENT ({doc['name']}):\n\n{doc['text']}"

    async def gen():
        async for chunk in llm.stream_chat(task, sys_msg, user_msg, big=big):
            yield chunk

    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")