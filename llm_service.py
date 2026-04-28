import os
import re
from datetime import datetime
from groq import Groq

# Configuration - Using the official Groq SDK
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Define the schema to provide context to the LLM
SCHEMA_CONTEXT = """
Table: transactions
Columns:
- id: SERIAL PRIMARY KEY
- user_id: INT
- amount: FLOAT
- category: VARCHAR (e.g., 'Food', 'Transport', 'Shopping', 'Utilities', 'Entertainment', 'Health')
- merchant: VARCHAR
- transaction_date: TIMESTAMP (Format: YYYY-MM-DD HH:MM:SS)
"""

def translate_nl_to_sql(question: str, user_id: int) -> str:
    """
    Converts a natural language question into a safe SQL SELECT statement.
    """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    prompt = f"""
    You are a SQL expert. Convert the following natural language question into a valid PostgreSQL query.
    
    {SCHEMA_CONTEXT}
    
    Constraints:
    1. Only return the SQL query. Do not include any explanation.
    2. The query MUST be a SELECT statement.
    3. Ensure the query filters by user_id = {user_id}.
    4. Current Date/Time: {current_date}. Use this for relative date queries (e.g., 'last month').
    5. 'last month' means transactions between the 1st and last day of the previous calendar month.
    
    Question: {question}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Current high-performance model on Groq
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        sql = response.choices[0].message.content.strip()
        
        # Safety & Validation
        return validate_sql(sql)
    except Exception as e:
        print(f"Groq SQL Generation Error: {e}")
        return None

def validate_sql(sql: str) -> str:
    """
    Ensures the generated SQL is safe and read-only.
    """
    # Remove markdown formatting if present
    sql = sql.replace("```sql", "").replace("```", "").strip()
    
    # Whitelist: Only SELECT queries
    if not sql.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    
    # Blacklist: Prohibited keywords
    prohibited = ["drop", "delete", "update", "insert", "alter", "truncate", "create", "grant"]
    for word in prohibited:
        if re.search(rf"\b{word}\b", sql.lower()):
            raise ValueError(f"Unsafe keyword detected: {word}")
            
    return sql

def generate_insight(question: str, results: list) -> str:
    """
    Converts raw database results into a human-readable insight.
    """
    if not results:
        return "I couldn't find any data matching your request."

    prompt = f"""
    You are a financial assistant. Summarize the following data in a friendly, conversational tone.
    
    User Question: {question}
    Data Results: {results}
    
    Provide a concise one or two-sentence insight.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq Insight Generation Error: {e}")
        return "Data retrieved, but I'm having trouble generating a summary right now."
