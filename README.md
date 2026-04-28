# Intelligent Query & Insight Engine

An AI-powered backend system that converts natural language financial queries into SQL, executes them, and enhances the results with LLM-generated insights.

## Features
- **NL to SQL**: Converts questions like "How much did I spend on food?" into SQLite queries.
- **LLM Insights**: Summarizes raw database results into natural language.
- **Safety First**: Whitelists only `SELECT` queries and blocks destructive keywords.
- **Caching**: In-memory caching for performance.
- **FastAPI**: Modern, fast (high-performance) web framework.

## Project Structure
```text
project/
├── main.py              # FastAPI application & endpoints
├── database.py          # SQLite connection & execution
├── llm_service.py       # NL-to-SQL & Insight logic
├── cache_service.py     # In-memory caching
├── schema.py            # Pydantic models
├── data_gen.py          # Mock data generator
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
3. **Set your API Key**:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
4. **Seed the Database**:
   ```bash
   python data_gen.py
   ```

## Running the API

Start the server using Uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

## Testing

You can use the provided test script:
```bash
python test_queries.py
```

Or use `curl`:
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "question": "How much did I spend on food last month?"}'
```

## Security Design
The system implements a read-only validation layer to ensure the LLM never executes destructive commands. Only `SELECT` statements are permitted, and keywords like `DROP`, `DELETE`, and `UPDATE` are strictly blocked.
