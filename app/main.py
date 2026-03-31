from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .db import get_schema_overview
from .knowledge_base import ingest_knowledge_base, save_uploaded_document
from .orchestrator import orchestrate_query


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Energy Expert Backend",
    description="Offline Conversational AI for Energy Data Analytics - Backend",
    version="0.4.0",
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
    diagnostics: Optional[Dict[str, Any]] = None
    kb_sources: Optional[List[str]] = None


class FeedbackRequest(BaseModel):
    question: str
    sql: str
    analysis: str
    rating: Literal["up", "down"]
    comment: Optional[str] = None
    diagnostics: Optional[Dict[str, Any]] = None
    kb_sources: Optional[List[str]] = None


# Helpers

def write_feedback_entry(payload: FeedbackRequest) -> Dict[str, Any]:
    feedback_path = Path(settings.FEEDBACK_LOG_PATH)
    feedback_path.parent.mkdir(parents=True, exist_ok=True)

    record = payload.model_dump()

    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "status": "ok",
        "saved_to": str(feedback_path),
    }


# Routes

@app.get("/")
def read_root():
    return {"message": "Energy Expert backend is running. See /health for status."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/schema")
def schema():
    schema_data = get_schema_overview()
    return {"schema": schema_data}


@app.post("/api/kb/ingest")
def ingest_kb():
    """Build/rebuild the FAISS vector index from files in knowledge_base/.
    Run this whenever you add or change documents.
    """
    return ingest_knowledge_base()


@app.post("/api/kb/upload")
async def upload_kb_documents(files: List[UploadFile] = File(...)):
    """Upload one or more supported documents (.pdf, .txt, .md) into the
    knowledge base folder. Automatically re-ingests the vector store after upload.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    saved_files: List[str] = []

    try:
        for upload in files:
            content = await upload.read()
            save_uploaded_document(upload.filename, content)
            saved_files.append(upload.filename)

        ingest_result = ingest_knowledge_base()

        return {
            "status": "ok",
            "saved_files": saved_files,
            "ingest_result": ingest_result,
        }
    except Exception as e:
        logger.exception("KB upload failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
def query_energy_expert(payload: QueryRequest):
    try:
        result = orchestrate_query(payload.question)
        return QueryResponse(
            question=payload.question,
            sql=result["sql"],
            rows=result["rows"],
            analysis=result["analysis"],
            diagnostics=result.get("diagnostics"),
            kb_sources=result.get("kb_sources"),
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
