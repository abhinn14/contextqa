from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from chat.src.document_ingestion.data_ingestion import ChatIngestor
from chat.src.document_chat.retrieval import ConversationalRAG
from langchain_core.messages import HumanMessage, AIMessage
from chat.exception.exception_handler import DocumentPortalException
from chat.utils.session_cleanup import cleanup_stale_sessions, touch_session_meta
from chat.logger import GLOBAL_LOGGER as log


# FastAPI initialization
app = FastAPI(title="ContextQA", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and templates
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Storage locations and TTL for cleanup
FAISS_BASE = BASE_DIR / "faiss_index"
DATA_BASE = BASE_DIR / "data"
SESSION_TTL_HOURS = 24

# Simple in-memory chat history
SESSIONS: Dict[str, List[dict]] = {}


# Adapters
class FastAPIFileAdapter:
    """Adapt FastAPI UploadFile to a simple object with .name and .getbuffer()."""
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename or "file"

    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()


# Models
class UploadResponse(BaseModel):
    session_id: str
    indexed: bool
    message: str | None = None


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str


# Routes
@app.get("/api/healthcheck")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload(files: List[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    try:
        # Prune stale sessions before accepting new uploads.
        cleanup_stale_sessions(FAISS_BASE, DATA_BASE, ttl_hours=SESSION_TTL_HOURS, sessions=SESSIONS)

        # Wrap FastAPI files to preserve filename/ext and provide a read buffer
        wrapped_files = [FastAPIFileAdapter(f) for f in files]

        ingestor = ChatIngestor(use_session_dirs=True)
        session_id = ingestor.session_id

        # Save, load, split, embed, and write FAISS index with MMR
        ingestor.built_retriver(
            uploaded_files=wrapped_files,
            search_type="mmr",
            fetch_k=20,
            lambda_mult=0.8
        )

        # Initialize empty history for this session
        SESSIONS[session_id] = []

        # Update metadata to reflect upload activity.
        touch_session_meta(FAISS_BASE / session_id, session_id)

        return UploadResponse(session_id=session_id, indexed=True, message="Indexing complete with MMR")
    except DocumentPortalException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id
    message = req.message.strip()
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=400, detail="Invalid or expired session_id. Re-upload documents.")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Prune stale sessions on access; this may drop old indexes and histories.
        cleanup_stale_sessions(FAISS_BASE, DATA_BASE, ttl_hours=SESSION_TTL_HOURS, sessions=SESSIONS)

        # Build RAG and load retriever from persisted FAISS with MMR
        rag = ConversationalRAG(session_id=session_id)
        index_path = str(FAISS_BASE / session_id)
        rag.load_retriever_from_faiss(
            index_path=index_path,
            search_type="mmr",
            fetch_k=20,
            lambda_mult=0.8
        )

        # Use simple in-memory history and convert to BaseMessage list
        simple = SESSIONS.get(session_id, [])
        lc_history = []
        for m in simple:
            role = m.get("role")
            content = m.get("content", "")
            if role == "user":
                lc_history.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_history.append(AIMessage(content=content))

        answer = rag.invoke(message, chat_history=lc_history)

        # Update history
        simple.append({"role": "user", "content": message})
        simple.append({"role": "assistant", "content": answer})
        SESSIONS[session_id] = simple

        # Update metadata to reflect recent usage for TTL cleanup.
        touch_session_meta(FAISS_BASE / session_id, session_id)

        return ChatResponse(answer=answer)
    except DocumentPortalException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
