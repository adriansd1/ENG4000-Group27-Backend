# Offline Conversational AI for Energy Data Analytics (Energy Expert)

**ENG 4000 Capstone Project — Team 27**
York University, Lassonde School of Engineering | Fall 2025 – Winter 2026

## Overview

Energy Expert is a fully offline, conversational AI system that enables telecom operations staff to query complex energy performance data using natural language. Built for PLC Group, it runs entirely on local hardware with no cloud dependencies, ensuring full data privacy and security.

The system uses a Dual RAG (Retrieval Augmented Generation) architecture that combines two reasoning pathways: a quantitative SQL pipeline for structured database queries, and a qualitative FAISS vector database for semantic document retrieval. Both pathways are powered by locally hosted language models through Ollama.

> **Note:** The frontend is integrated directly into this repository under `frontend/`. The separate frontend repo is not in use.

## Features

- Full natural language to SQL query pipeline with automated diagnostic analysis
- FAISS based semantic document retrieval from engineering documentation
- Next.js chatbot frontend fully connected to the backend API
- Multilayer SQL safety validation (zero breach record across all testing)
- PDF upload and ingestion for the knowledge base
- User feedback logging endpoint
- Complete offline operation via Ollama (Llama 3.1 8B), no external API dependencies

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI v0.115.5, Uvicorn |
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Database | PostgreSQL |
| Vector DB | FAISS (faiss-cpu) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Llama 3.1 8B via Ollama (local, offline) |
| PDF Parsing | pypdf |

## Repository Structure

```
ENG4000-Group27-Backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Environment variables and settings
│   ├── db.py                  # PostgreSQL connection, schema introspection, SQL execution
│   ├── evaluation.py          # Query evaluation utilities
│   ├── knowledge_base.py      # FAISS vector DB, PDF ingestion, semantic retrieval
│   ├── llm.py                 # Ollama LLM interface (Llama 3.1 8B)
│   ├── main.py                # FastAPI app, API endpoints
│   └── orchestrator.py        # Dual RAG pipeline coordination
├── db/
│   ├── full_schema.sql        # Complete database schema
│   ├── site_metadata.sql      # Site metadata table
│   ├── site_inventory.sql     # Equipment inventory table
│   ├── performance_daily_data.sql  # Daily energy performance data
│   ├── daily_alarms.sql       # Alarm records table
│   └── seed_mock_data.sql     # Mock dataset for development
├── frontend/
│   ├── src/                   # Next.js source code
│   ├── package.json           # Node.js dependencies
│   ├── tailwind.config.ts     # Tailwind CSS configuration
│   ├── next.config.js         # Next.js configuration
│   └── tsconfig.json          # TypeScript configuration
├── knowledge_base/            # Engineering PDFs and policy documents
├── tests/
│   └── test_backend.py        # Backend test suite
├── .env.example               # Environment variable template
├── requirements.txt           # Python dependencies
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root status endpoint |
| GET | `/health` | Health check (`{"status": "ok"}`) |
| GET | `/schema` | Returns PostgreSQL database schema overview |
| POST | `/api/query` | Accepts `{"question": "..."}`, returns SQL, data rows, and diagnostic analysis |
| POST | `/api/kb/ingest` | Triggers FAISS vector index rebuild from knowledge base documents |
| POST | `/api/kb/upload` | Upload PDF files to the knowledge base |
| POST | `/api/feedback` | Logs user feedback on query responses |

## Installation and Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Ollama with Llama 3.1 8B model pulled locally

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/adriansd1/ENG4000-Group27-Backend.git
cd ENG4000-Group27-Backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up the database
psql -U postgres -f db/full_schema.sql
psql -U postgres -f db/seed_mock_data.sql

# Configure environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials and Ollama settings

# Start Ollama with Llama 3.1 8B
ollama pull llama3.1:8b
ollama serve

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000` and connects to the backend at `http://localhost:8000`.

## Testing

```bash
# Run backend tests
pytest tests/test_backend.py -v

# Verify endpoints manually
curl http://localhost:8000/health
curl http://localhost:8000/schema
curl -X POST http://localhost:8000/api/query -H "Content-Type: application/json" -d '{"question": "What is the average diesel consumption across all sites?"}'
```

## Team

| Member | Role |
|--------|------|
| Dilpreet Bansi | Backend Development |
| Adrian Sam Daliri | Backend / Integration Lead |
| Nathan Binu Edappilly | Backend / Knowledge Base / LLM Integration |
| Humayun Ejaz | Backend / Database |
| Mark Farid | Backend / Testing |
| Umer Shaikh | Frontend / UI Development |

**Supervisor:** Professor Emily Kuang
**Industry Partner:** PLC Group

## License

This project was developed as part of the ENG 4000 Capstone course at York University's Lassonde School of Engineering.
