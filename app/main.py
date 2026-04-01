import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List, Dict

from .config import settings
from .db import get_schema_overview
from .orchestrator import orchestrate_query
from .knowledge_base import ingest_knowledge_base, save_uploaded_document

app = FastAPI(
    title="Energy Expert Backend",
    description="Offline Conversational AI for Energy Data Analytics - Backend",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql: str
    rows: List[Dict[str, Any]]
    analysis: str


class FeedbackRequest(BaseModel):
    question: str
    sql: str
    analysis: str
    rating: str
    feedback_text: str | None = None


def write_feedback_entry(payload: FeedbackRequest):
    feedback_path = Path(settings.FEEDBACK_LOG_PATH)
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    entry = payload.model_dump()

    with feedback_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return {"status": "ok", "path": str(feedback_path)}


@app.get("/")
def read_root():
    return {
        "message": "Energy Expert backend is running. See /health for status."
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/schema")
def schema():
    """
    Return a human-readable overview of the database schema.
    """
    schema_data = get_schema_overview()
    return {"schema": schema_data}


@app.post("/api/kb/ingest")
def ingest_kb():
    """
    Build/rebuild the FAISS vector index from files in knowledge_base/.
    """
    return ingest_knowledge_base()


@app.post("/api/kb/upload")
async def upload_kb_file(file: UploadFile = File(...)):
    """
    Upload a KB document, save it locally, and rebuild the vector index.
    """
    try:
        content = await file.read()
        saved_path = save_uploaded_document(file.filename or "", content)
        ingest_result = ingest_knowledge_base()
        return {
            "status": "ok",
            "filename": Path(saved_path).name,
            "path": saved_path,
            "ingest": ingest_result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()


@app.post("/api/query", response_model=QueryResponse)
def query_energy_expert(payload: QueryRequest):
    try:
        result = orchestrate_query(payload.question)

        return QueryResponse(
            question=payload.question,
            sql=result["sql"],
            rows=result["rows"],
            analysis=result["analysis"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
def submit_feedback(payload: FeedbackRequest):
    """Logs user feedback for future review / tuning."""
    try:
        return write_feedback_entry(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
