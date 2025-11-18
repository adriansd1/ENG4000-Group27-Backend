# Offline Conversational AI for Energy Data Analytics 

This repository contains the backend for the **Offline Conversational AI for Energy Data Analytics**, an offline conversational AI system designed to help telecom engineering teams analyze energy performance data using natural language.  
At this stage, the backend is in its initial setup phase and provides the basic FastAPI application structure along with health-check functionality.

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

This first stage lays the foundation by initializing the backend project structure.

---

## Features Available at This Stage

### FastAPI Initialization  
A minimal FastAPI application is set up with two basic routes:

- GET / — a welcome endpoint confirming the backend is running  
- GET /health — a simple status endpoint returning {"status": "ok"}  

These routes ensure the project starts successfully and can respond to HTTP requests.

---

## Installation & Running Instructions

### 1. Clone the repository
git clone <your-backend-repo-url> ENG4000-Group27-Backend
cd ENG4000-Group27-Backend

### 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

---

## Test the Endpoints

- http://localhost:8000  
- http://localhost:8000/health  

If both return valid responses, your backend is set up correctly.

---

## What Comes Next

Future stages will introduce:

- PostgreSQL integration  
- Schema introspection  
- Local LLM (Ollama) integration  
- Text-to-SQL capabilities  
- Knowledge base retrieval  
- Feedback system  
- Swagger API documentation  

This README reflects the project in its simplest foundational state.
