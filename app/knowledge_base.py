# import os
# import json
# import time
# import logging
# from dataclasses import dataclass
# from typing import List, Dict, Optional, Tuple

# import numpy as np
# import faiss
# from pypdf import PdfReader
# from app.config import Settings
# from sentence_transformers import SentenceTransformer


# logger = logging.getLogger(__name__)

# # Folder with your unstructured docs (.txt, .md)
# KB_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

# # Folder where we store FAISS index + metadata
# VS_DIR = os.path.join(os.path.dirname(__file__), "..", "vector_store")
# INDEX_PATH = os.path.join(VS_DIR, "kb.index")
# META_PATH = os.path.join(VS_DIR, "kb_meta.json")

# # Default embedding model (downloads once, then can run offline)
# DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"


# @dataclass
# class KnowledgeChunk:
#     chunk_id: int
#     source: str
#     text: str


# def ensure_dir(path: str) -> None:
#     os.makedirs(path, exist_ok=True)


# def list_kb_files() -> List[str]:
#     if not os.path.isdir(KB_DIR):
#         return []
#     files = []
#     for fname in os.listdir(KB_DIR):
#         if fname.lower().endswith((".txt", ".md")):
#             files.append(os.path.join(KB_DIR, fname))
#     return sorted(files)


# def read_text_file(path: str) -> str:
#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         return f.read()


# def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
#     """
#     Safe character-based chunking that always makes progress (prevents infinite loops).
#     """
#     text = (text or "").strip()
#     if not text:
#         return []

#     chunks: List[str] = []
#     n = len(text)
#     start = 0

#     while start < n:
#         end = min(n, start + chunk_size)
#         chunk = text[start:end].strip()
#         if chunk:
#             chunks.append(chunk)

#         if end >= n:
#             break  # reached the end

#         # next window start with overlap, but guarantee forward progress
#         next_start = max(0, end - overlap)
#         if next_start <= start:
#             next_start = end  # force progress if overlap would stall

#         start = next_start

#     return chunks


# _MODEL_CACHE: Dict[str, SentenceTransformer] = {}


# def get_model(model_name: str = DEFAULT_EMBED_MODEL) -> SentenceTransformer:
#     """
#     Cache model in-process so we don't reload it every time.
#     """
#     if model_name not in _MODEL_CACHE:
#         logger.info("Loading embedding model: %s", model_name)
#         _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
#         logger.info("Embedding model loaded: %s", model_name)
#     return _MODEL_CACHE[model_name]


# def embed_texts(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
#     """
#     Returns float32 numpy array of normalized embeddings.
#     Normalized -> inner product equals cosine similarity.
#     """
#     vecs = model.encode(
#         texts,
#         show_progress_bar=False,
#         normalize_embeddings=True,
#     )
#     return np.asarray(vecs, dtype=np.float32)


# def build_index(vectors: np.ndarray) -> faiss.Index:
#     dim = vectors.shape[1]
#     index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized + inner product
#     index.add(vectors)
#     return index


# def save_index(index: faiss.Index, meta: List[Dict]) -> None:
#     ensure_dir(VS_DIR)
#     faiss.write_index(index, INDEX_PATH)
#     with open(META_PATH, "w", encoding="utf-8") as f:
#         json.dump(meta, f, indent=2)


# def load_index() -> Tuple[Optional[faiss.Index], Optional[List[Dict]]]:
#     if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
#         return None, None

#     index = faiss.read_index(INDEX_PATH)
#     with open(META_PATH, "r", encoding="utf-8") as f:
#         meta = json.load(f)
#     return index, meta


# def ingest_knowledge_base(model_name: str = DEFAULT_EMBED_MODEL) -> Dict:
#     """
#     Build/rebuild the FAISS index from knowledge_base/ docs.
#     Generates:
#       - vector_store/kb.index
#       - vector_store/kb_meta.json
#     """
#     t0 = time.time()
#     logger.info("KB ingest started. KB_DIR=%s VS_DIR=%s", KB_DIR, VS_DIR)

#     files = list_kb_files()
#     logger.info("KB files found: %d", len(files))

#     if not files:
#         return {
#             "status": "no_files",
#             "message": "No .txt/.md files found in knowledge_base/ (create it and add docs).",
#             "seconds_elapsed": round(time.time() - t0, 3),
#         }

#     model = get_model(model_name)

#     meta: List[Dict] = []
#     chunk_texts: List[str] = []

#     chunk_id = 0
#     for path in files:
#         source = os.path.basename(path)
#         text = read_text_file(path)
#         chunks = chunk_text(text)

#         logger.info("Chunked %s -> %d chunks", source, len(chunks))

#         for c in chunks:
#             meta.append({"chunk_id": chunk_id, "source": source, "text": c})
#             chunk_texts.append(c)
#             chunk_id += 1

#     if not chunk_texts:
#         return {
#             "status": "no_chunks",
#             "message": "Docs were found but produced no chunks. Check file contents.",
#             "files": len(files),
#             "seconds_elapsed": round(time.time() - t0, 3),
#         }

#     logger.info("Embedding %d chunks...", len(chunk_texts))
#     t_embed = time.time()
#     vectors = embed_texts(model, chunk_texts)
#     logger.info("Embedding done in %.3fs. vectors.shape=%s", time.time() - t_embed, getattr(vectors, "shape", None))

#     logger.info("Building FAISS index...")
#     index = build_index(vectors)

#     logger.info("Saving FAISS index + metadata...")
#     save_index(index, meta)

#     seconds = round(time.time() - t0, 3)
#     logger.info("KB ingest finished in %.3fs. index=%s meta=%s", seconds, INDEX_PATH, META_PATH)

#     return {
#         "status": "ok",
#         "files": len(files),
#         "chunks": len(meta),
#         "vectors_shape": list(vectors.shape),
#         "index_path": INDEX_PATH,
#         "meta_path": META_PATH,
#         "index_exists": os.path.exists(INDEX_PATH),
#         "meta_exists": os.path.exists(META_PATH),
#         "seconds_elapsed": seconds,
#     }


# def retrieve_chunks(question: str, k: int = 4, model_name: str = DEFAULT_EMBED_MODEL) -> List[KnowledgeChunk]:
#     """
#     Retrieve top-k most relevant chunks from FAISS.
#     Returns [] if the index hasn't been built yet.
#     """
#     index, meta = load_index()
#     if index is None or meta is None:
#         return []

#     model = get_model(model_name)
#     q_vec = embed_texts(model, [question])  # shape (1, dim)

#     scores, ids = index.search(q_vec, k)
#     results: List[KnowledgeChunk] = []

#     for idx in ids[0]:
#         if idx == -1:
#             continue
#         m = meta[int(idx)]
#         results.append(KnowledgeChunk(chunk_id=m["chunk_id"], source=m["source"], text=m["text"]))

#     return results

import os
import json
import time
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


from .config import settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = str((BASE_DIR / settings.KB_DIR).resolve())
VS_DIR = str((BASE_DIR / settings.VECTOR_STORE_DIR).resolve())

INDEX_PATH = os.path.join(VS_DIR, "kb.index")
META_PATH = os.path.join(VS_DIR, "kb_meta.json")

DEFAULT_EMBED_MODEL = settings.EMBED_MODEL


@dataclass
class KnowledgeChunk:
    chunk_id: int
    source: str
    text: str
    document_type: str = "unknown"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def allowed_extension(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in settings.KB_ALLOWED_EXTENSIONS


def list_kb_files() -> List[str]:
    if not os.path.isdir(KB_DIR):
        return []

    files = []
    for fname in os.listdir(KB_DIR):
        if allowed_extension(fname):
            files.append(os.path.join(KB_DIR, fname))
    return sorted(files)


def read_pdf_file(path: str) -> str:
    reader = PdfReader(path)
    pages: List[str] = []

    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"[Page {idx}]\n{text}")

    return "\n\n".join(pages)


def read_document(path: str) -> str:
    suffix = Path(path).suffix.lower()

    if suffix in (".txt", ".md"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if suffix == ".pdf":
        return read_pdf_file(path)

    return ""


def classify_document_type(filename: str) -> str:
    name = filename.lower()

    if "troubleshooting" in name:
        return "troubleshooting_guide"
    if "alarm" in name:
        return "alarm_reference"
    if "specification" in name or "spec" in name:
        return "specification"
    if "manual" in name or "operation" in name or "iom" in name:
        return "manual"
    if "checklist" in name:
        return "checklist"
    return "general"


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Safe character-based chunking that always makes progress.
    """
    chunk_size = chunk_size or settings.KB_CHUNK_SIZE
    overlap = overlap or settings.KB_CHUNK_OVERLAP

    text = (text or "").strip()
    if not text:
        return []

    chunks: List[str] = []
    n = len(text)
    start = 0

    while start < n:
        end = min(n, start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= n:
            break

        next_start = max(0, end - overlap)
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


_MODEL_CACHE: Dict[str, SentenceTransformer] = {}


def get_model(model_name: str = DEFAULT_EMBED_MODEL) -> SentenceTransformer:
    if model_name not in _MODEL_CACHE:
        logger.info("Loading embedding model: %s", model_name)
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
        logger.info("Embedding model loaded: %s", model_name)
    return _MODEL_CACHE[model_name]


def embed_texts(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
    vecs = model.encode(
        texts,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return np.asarray(vecs, dtype=np.float32)


def build_index(vectors: np.ndarray) -> faiss.Index:
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    return index


def save_index(index: faiss.Index, meta: List[Dict]) -> None:
    ensure_dir(VS_DIR)
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def load_index() -> Tuple[Optional[faiss.Index], Optional[List[Dict]]]:
    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
        return None, None

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta


def save_uploaded_document(filename: str, content: bytes) -> str:
    if not allowed_extension(filename):
        raise ValueError(f"Unsupported file type for upload: {filename}")

    ensure_dir(KB_DIR)

    safe_name = Path(filename).name
    target_path = os.path.join(KB_DIR, safe_name)

    with open(target_path, "wb") as f:
        f.write(content)

    return target_path


def ingest_knowledge_base(model_name: str = DEFAULT_EMBED_MODEL) -> Dict:
    """
    Build/rebuild the FAISS index from knowledge_base/ documents.
    Supports .txt, .md, and .pdf files.
    """
    t0 = time.time()
    logger.info("KB ingest started. KB_DIR=%s VS_DIR=%s", KB_DIR, VS_DIR)

    files = list_kb_files()
    logger.info("KB files found: %d", len(files))

    if not files:
        return {
            "status": "no_files",
            "message": "No supported documents found in knowledge_base/ (.txt, .md, .pdf).",
            "seconds_elapsed": round(time.time() - t0, 3),
        }

    model = get_model(model_name)

    meta: List[Dict] = []
    chunk_texts: List[str] = []
    chunk_id = 0

    for path in files:
        source = os.path.basename(path)
        document_type = classify_document_type(source)
        text = read_document(path)
        chunks = chunk_text(text)

        logger.info("Chunked %s -> %d chunks", source, len(chunks))

        for local_idx, chunk in enumerate(chunks):
            meta.append({
                "chunk_id": chunk_id,
                "source": source,
                "document_type": document_type,
                "chunk_number": local_idx,
                "text": chunk,
            })
            chunk_texts.append(chunk)
            chunk_id += 1

    if not chunk_texts:
        return {
            "status": "no_chunks",
            "message": "Documents were found but produced no chunks. Check file contents.",
            "files": len(files),
            "seconds_elapsed": round(time.time() - t0, 3),
        }

    logger.info("Embedding %d chunks...", len(chunk_texts))
    vectors = embed_texts(model, chunk_texts)

    logger.info("Building FAISS index...")
    index = build_index(vectors)

    logger.info("Saving FAISS index + metadata...")
    save_index(index, meta)

    seconds = round(time.time() - t0, 3)
    logger.info("KB ingest finished in %.3fs.", seconds)

    return {
        "status": "ok",
        "files": len(files),
        "chunks": len(meta),
        "vectors_shape": list(vectors.shape),
        "index_path": INDEX_PATH,
        "meta_path": META_PATH,
        "index_exists": os.path.exists(INDEX_PATH),
        "meta_exists": os.path.exists(META_PATH),
        "seconds_elapsed": seconds,
    }


def retrieve_chunks(
    question: str,
    k: int = None,
    model_name: str = DEFAULT_EMBED_MODEL,
) -> List[KnowledgeChunk]:
    """
    Retrieve top-k most relevant chunks from FAISS.
    Returns [] if the index has not been built yet.
    """
    k = k or settings.KB_TOP_K

    index, meta = load_index()
    if index is None or meta is None:
        return []

    model = get_model(model_name)
    q_vec = embed_texts(model, [question])

    scores, ids = index.search(q_vec, k)
    results: List[KnowledgeChunk] = []

    for idx in ids[0]:
        if idx == -1:
            continue
        m = meta[int(idx)]
        results.append(
            KnowledgeChunk(
                chunk_id=m["chunk_id"],
                source=m["source"],
                text=m["text"],
                document_type=m.get("document_type", "unknown"),
            )
        )

    return results
