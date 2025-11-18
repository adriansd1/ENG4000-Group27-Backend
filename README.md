
# Offline Conversational AI for Energy Data Analytics 

This repository contains the backend for the **Offline Conversational AI for Energy Data Analytics**, an offline conversational AI system designed to help telecom engineering teams analyze energy performance data using natural language.  
At this stage, the backend now includes the initial FastAPI structure **plus PostgreSQL connectivity and dynamic schema introspection**, enabling the system to read database tables automatically.

---

## Project Overview

This Project aims to allow users to interact with telecom site energy data through natural language queries.  
The final backend will eventually include:

- Local LLM interaction  
- SQL generation from natural language  
- PostgreSQL data integration  
- Diagnostic reasoning  
- Domain knowledge augmentation  
- Feedback loop for improvements  

This stage expands the foundation by adding database support and schema discovery.

---

## Features Available at This Stage

### FastAPI Initialization  
A minimal FastAPI application is set up with routes such as:

- GET / — a welcome endpoint confirming the backend is running  
- GET /health — a simple status endpoint returning {"status": "ok"}
- GET /schema — returns the full PostgreSQL database structure using dynamic schema introspection
 

### PostgreSQL Connection  
The backend now supports PostgreSQL through environment-based configuration.

### Dynamic Schema Introspection  
A new endpoint allows the system to automatically read the structure of all tables in the connected PostgreSQL database.

---

## Installation & Running Instructions

### 1. Clone the repository
```bash
git clone https://github.com/adriansd1/ENG4000-Group27-Backend/ ENG4000-Group27-Backend
cd ENG4000-Group27-Backend
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up the PostgreSQL database  
Run the provided SQL schema files (located in /db):

```bash
psql -U postgres -d energy_db -f db/full_schema.sql
```

### 5. Configure environment variables  
Copy `.env.example` to `.env` and update:

```
POSTGRES_URL=postgresql://postgres:<password>@localhost:5432/PLC_db
```

### 6. Start the backend server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Test the Endpoints

- http://localhost:8000  
- http://localhost:8000/health  
- http://localhost:8000/schema  

If these return valid responses, your backend is connected and functioning properly.

---

## What Comes Next

Future stages will introduce:

- Local LLM (Ollama) integration  
- Text-to-SQL capabilities  
- Knowledge base retrieval  
- Feedback system  
- Swagger API documentation  

This README reflects the project with PostgreSQL integration and schema introspection included.
