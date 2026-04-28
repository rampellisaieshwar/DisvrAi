from pydantic import BaseModel
from typing import List, Optional, Any

class QueryRequest(BaseModel):
    user_id: int
    question: str

class QueryResponse(BaseModel):
    question: str
    sql: Optional[str] = None
    data: Optional[List[Any]] = None
    insight: str
    cached: bool = False
    error: Optional[str] = None
