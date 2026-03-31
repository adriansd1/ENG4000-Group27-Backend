from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List, Dict

from .config import settings
from .db import get_schema_overview
from .orchestrator import orchestrate_query
from .knowledge_base import ingest_knowledge_base

import logging
logging.basicConfig(level=logging.INFO)


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
    return {"message": "Energy Expert backend is running. See /health for status."}


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
    Run this whenever you add or change documents.
    """
    return ingest_knowledge_base()


@app.post("/api/query", response_model=QueryResponse)
def query_energy_expert(payload: QueryRequest):
    try:
        sql, rows, analysis = orchestrate_query(payload.question)
        return QueryResponse(question=payload.question, sql=sql, rows=rows, analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
