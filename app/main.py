from fastapi import FastAPI, HTTPException
from .db import get_schema_overview

from pydantic import BaseModel
from typing import Any, List, Dict

from .orchestrator import generate_sql_for_question, run_sql, generate_analysis, orchestrate_query

app = FastAPI(
    title="Energy Expert Backend",
    description="Offline Conversational AI for Energy Data Analytics - Backend",
    version="0.3.0",
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

@app.post("/api/query", response_model=QueryResponse)
def query_energy_expert(payload: QueryRequest):
    try:
        sql, rows, analysis = orchestrate_query(payload.question)
        return QueryResponse(
            question=payload.question,
            sql=sql,
            rows=rows,
            analysis=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))