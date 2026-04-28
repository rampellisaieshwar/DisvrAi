from fastapi import FastAPI, HTTPException
from schema import QueryRequest, QueryResponse
from database import execute_query
from llm_service import translate_nl_to_sql, generate_insight
from cache_service import query_cache
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Intelligent Query & Insight Engine")

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Main endpoint that processes NL queries.
    Pipeline: Cache -> NL2SQL -> DB -> LLM Insight -> Return
    """
    # 1. Check Cache
    cached_result = query_cache.get(request.user_id, request.question)
    if cached_result:
        logger.info(f"Cache hit for question: {request.question}")
        cached_result["cached"] = True
        return cached_result

    try:
        # 2. Convert NL to SQL
        sql = translate_nl_to_sql(request.question, request.user_id)
        if not sql:
            return QueryResponse(
                question=request.question,
                insight="I'm sorry, I couldn't understand how to convert your question into a database query.",
                error="SQL generation failed"
            )

        # 3. Execute SQL
        logger.info(f"Executing SQL: {sql}")
        data = execute_query(sql)

        # 4. Generate Insight
        insight = generate_insight(request.question, data)

        response = QueryResponse(
            question=request.question,
            sql=sql,
            data=data,
            insight=insight,
            cached=False
        )

        # 5. Store in Cache
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
