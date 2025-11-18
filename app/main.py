from fastapi import FastAPI
from .db import get_schema_overview

app = FastAPI(
    title="Energy Expert Backend",
    description="Offline Conversational AI for Energy Data Analytics - Backend",
    version="0.1.0",
)


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