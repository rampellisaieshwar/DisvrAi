# Intelligent Query & Insight Engine

An AI-powered backend system that converts natural language financial queries into SQL, executes them, and enhances the results with LLM-generated insights.

## Features
- **NL to SQL**: Converts questions like "How much did I spend on food?" into PostgreSQL queries.
- **LLM Insights**: Summarizes raw database results into natural language.
- **Safety First**: Whitelists only `SELECT` queries and blocks destructive keywords.
- **Semantic Caching**: In-memory vector embeddings (via `fastembed`) to catch identically-meaning questions.
- **FastAPI**: Modern, fast (high-performance) web framework.

## Project Structure
```text
project/
├── main.py              # FastAPI application & endpoints
├── database.py          # PostgreSQL (Supabase) connection & execution
├── llm_service.py       # NL-to-SQL & Insight logic
├── cache_service.py     # In-memory caching
├── schema.py            # Pydantic models
├── test_queries.py      # Manual testing script
├── requirements.txt     # Dependencies
└── interview_notes.md   # Prep for interview questions
```

## Setup & Installation

1. **Clone the repository** (or navigate to the folder).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   ```bash
   export GROQ_API_KEY='your-groq-api-key'
   export DATABASE_URL='postgresql://postgres.project-ref:password@aws-0-region.pooler.supabase.com:6543/postgres'
   ```

## Running the API

Start the server locally using Uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

Alternatively, the project is structured to be deployed directly on **Render** using the start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Testing

You can use the provided test script:
```bash
python test_queries.py
```

Or use `curl` to hit the live Render deployment (if applicable) or your local server:
```bash
curl -X POST "https://disvrai-api.onrender.com/query" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "question": "How much did I spend on food last month?"}'
```

## Security Design
The system implements a read-only validation layer to ensure the LLM never executes destructive commands. Only `SELECT` statements are permitted, and keywords like `DROP`, `DELETE`, and `UPDATE` are strictly blocked.
