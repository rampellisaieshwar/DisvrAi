import os
import re
import json
from datetime import datetime
from groq import Groq
from database import execute_query

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

def run_agent(question: str, user_id: int):
    """
    Autonomous ReAct Agent Loop.
    The LLM decides when to query the database, validates errors, and formulates the final answer.
    Returns: (sql_used, data_fetched, final_insight)
    """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    system_prompt = f"""
    You are an autonomous financial AI agent. Your goal is to answer the user's questions about their transactions.
    You have access to a PostgreSQL database via the `query_database` tool.
    
    {SCHEMA_CONTEXT}
    
    Constraints:
    1. The user's ID is {user_id}. You MUST filter all queries by user_id = {user_id}.
    2. Current Date/Time: {current_date}. Use this for relative dates ('last month', etc.).
    3. You can only use SELECT queries. Do NOT attempt to modify data.
    4. If the database returns an error, use the error message to fix your SQL query and call the tool again!
    5. Once you have the data, provide a friendly, concise, 1-2 sentence conversational answer directly to the user.
    """

    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Execute a PostgreSQL SELECT query to retrieve transaction data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "The raw PostgreSQL SELECT query to execute.",
                        }
                    },
                    "required": ["sql_query"],
                },
            },
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    last_sql_used = None
    last_data_fetched = None

    # ReAct Loop: Allow up to 5 iterations to prevent infinite loops
    for step in range(5):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.1
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # If the model wants to call a tool
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "query_database":
                        function_args = json.loads(tool_call.function.arguments)
                        sql = function_args.get("sql_query")
                        last_sql_used = sql
                        
                        try:
                            # 1. Validate SQL locally for safety
                            safe_sql = validate_sql(sql)
                            # 2. Execute SQL against DB
                            result_data = execute_query(safe_sql)
                            last_data_fetched = result_data
                            tool_result = json.dumps(result_data, default=str) # Convert datetimes to strings
                        except Exception as e:
                            # If validation or execution fails, feed the error back to the LLM so it can correct it!
                            tool_result = f"Error: {str(e)}"
                            
                        # Append the tool result to the conversation
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": "query_database",
                            "content": tool_result,
                        })
            else:
                # If there are no tool calls, the agent has formulated its final answer!
                final_insight = response_message.content.strip()
                return last_sql_used, last_data_fetched, final_insight
                
        except Exception as e:
            print(f"Agent Loop Error: {e}")
            return last_sql_used, last_data_fetched, "An error occurred while the agent was reasoning."
            
    return last_sql_used, last_data_fetched, "The agent reached the maximum number of thought steps without finding an answer."
