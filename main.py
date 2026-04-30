from fastapi import FastAPI, HTTPException
from schema import QueryRequest, QueryResponse
from database import execute_query
from llm_service import run_agent
from cache_service import query_cache
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Intelligent Query & Insight Engine")

@app.get("/")
def health_check():
    return {"status": "healthy", "message": """API is running.To test api go to docs in POST 'Try it out' button and enter your question in JSON format {\"user_id\": 1, \"question\": \"What is my total spending?"}"""}

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Main endpoint that processes NL queries.
    Pipeline: Cache -> Autonomous Agent (ReAct Loop) -> Return
    """
    # 1. Check Cache
    cached_result, is_semantic = query_cache.get(request.user_id, request.question)
    if cached_result:
        if is_semantic:
            logger.info(f"Semantic Cache hit for question: {request.question}")
        else:
            logger.info(f"Cache hit for question: {request.question}")
        cached_result["cached"] = True
        return cached_result

    try:
        # 2. Run Autonomous Agent
        sql, data, insight = run_agent(request.question, request.user_id)
        
        response = QueryResponse(
            question=request.question,
            sql=sql,
            data=data,
            insight=insight,
            cached=False
        )

        # 3. Store in Cache (only if it successfully found data/sql)
        if sql is not None:
            query_cache.set(request.user_id, request.question, response.dict())
        
        return response

    except ValueError as ve:
        # Catch safety/validation errors
        logger.error(f"Validation Error: {ve}")
        return QueryResponse(
            question=request.question,
            insight="I'm sorry, but your query was flagged for safety or security reasons.",
            error=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        return QueryResponse(
            question=request.question,
            insight="An unexpected error occurred while processing your request.",
            error="Internal Server Error"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
