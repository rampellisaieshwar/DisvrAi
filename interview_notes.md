# Interview Notes: Intelligent Query & Insight Engine

This document provides high-level talking points and technical justifications for the choices made in this project. Use these to defend your implementation during the interview.

## 1. The Core Sentence (The "Elevator Pitch")
> "I built a modular pipeline that converts natural language into SQL using an LLM, validates it for security, executes it on a Supabase PostgreSQL database, and then uses another LLM pass to generate human-friendly insights. I also implemented an in-memory cache to optimize performance for repeated queries, and deployed the entire service to Render."

## 2. Key Technical Choices & Justifications

### Why PostgreSQL (Supabase)?
- **Justification**: "I initially started with a local SQLite prototype for rapid iteration, but I quickly migrated the architecture to a remote PostgreSQL database on Supabase using `psycopg2`. This makes the API production-ready, allows for connection pooling (IPv4 compatibility on Render), and provides a much more robust foundation for scaling."

### How did you handle SQL Injection/Safety?
- **Justification**: "Relying on an LLM for SQL is powerful but risky. I implemented a two-layer safety check:
    1. **Whitelist**: Only `SELECT` statements are allowed.
    2. **Blacklist**: I use regex to explicitly block destructive keywords like `DROP`, `DELETE`, or `UPDATE`. 
    - *Pro Tip*: In a production system, I'd also use a read-only database user and potentially a SQL parser (like `sqlglot`) to validate the AST (Abstract Syntax Tree)."

### How did you handle Date Logic (e.g., "last month")?
- **Justification**: "I pass the current timestamp into the LLM prompt. This provides the model with the necessary context to calculate relative dates (like 'last month' or 'yesterday') accurately within the SQL query it generates."

### Why this Caching strategy?
- **Justification**: "I used an in-memory cache keyed by `(user_id, question)`. This ensures that if the same user asks the same question, we bypass both the LLM and the Database entirely. For a distributed system, I would transition this to **Redis**."

### What if the LLM fails?
- **Justification**: "I implemented structured error handling. If the LLM produces invalid SQL or fails to respond, the API returns a friendly natural language error to the user instead of a 500 Internal Server Error."

## 3. Potential Follow-up Questions

### "How would you scale this to millions of transactions?"
- **Answer**: "Since the database is already running on a remote PostgreSQL instance, I would focus on creating indexes on `user_id` and `transaction_date` to speed up queries. I would also transition the local in-memory cache to a distributed **Redis** cache. Finally, I'd consider adding a vector database to help the LLM find the most relevant schema parts dynamically if the database schema grows to hundreds of tables."

### "How do you ensure the LLM doesn't make up categories?"
- **Answer**: "I include the valid categories in the prompt context. If categories were dynamic, I would fetch the distinct categories from the DB first and inject them into the prompt dynamically."
