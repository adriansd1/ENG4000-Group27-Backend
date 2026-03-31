from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List, Dict

from .db import get_schema_overview
from .orchestrator import orchestrate_query
from .knowledge_base import ingest_knowledge_base

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
