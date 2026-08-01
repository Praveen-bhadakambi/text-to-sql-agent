"""
Text-to-SQL Query Agent
========================
FastAPI backend that converts natural language questions into
SQLite SQL queries using Google Gemini, executes them safely,
and returns structured JSON results.

Run:
    uvicorn main:app --reload

API Docs (auto-generated):
    http://localhost:8000/docs
"""

import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from database import get_connection, DB_PATH
from schema_inspector import get_schema_description
from sql_validator import validate_query
from llm_service import generate_sql


# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Text-to-SQL Query Agent",
    description=(
        "Convert plain English questions into SQL queries using Gemini AI. "
        "Supports schema introspection, safety validation, and query history."
    ),
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/home", include_in_schema=False)
def landing_page():
    return FileResponse("static/index.html")

# Allow all origins for local development (restrict this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models (request / response shapes) ────────────────────────────────
class QueryRequest(BaseModel):
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Who are the top 3 highest paid employees?"
            }
        }


class QueryResponse(BaseModel):
    question: str
    generated_sql: str
    results: list
    row_count: int
    executed_at: str


class HistoryItem(BaseModel):
    id: int
    question: str
    generated_sql: str
    row_count: int
    created_at: str


# ── Helper: save every query to history table ──────────────────────────────────
def _ensure_history_table():
    """Creates query_history table if it does not exist yet."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            question      TEXT    NOT NULL,
            generated_sql TEXT    NOT NULL,
            row_count     INTEGER DEFAULT 0,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _save_history(question: str, sql: str, row_count: int):
    """Inserts one row into query_history."""
    _ensure_history_table()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO query_history (question, generated_sql, row_count) VALUES (?, ?, ?)",
        (question, sql, row_count),
    )
    conn.commit()
    conn.close()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check — confirms the server is running."""
    return {
        "status": "running",
        "message": "Text-to-SQL Agent is live. Visit /docs for the API explorer.",
    }


@app.get("/schema", tags=["Database"])
def get_schema():
    """
    Returns the current database schema.
    Useful for understanding what questions you can ask.
    """
    schema = get_schema_description()
    return {"schema": schema}


@app.post("/query", response_model=QueryResponse, tags=["Core"])
def query(request: QueryRequest):
    """
    Main endpoint. Converts a natural language question to SQL and executes it.

    Steps:
      1. Read schema from database
      2. Send question + schema to Gemini → get SQL
      3. Validate SQL (block dangerous operations)
      4. Execute SQL on SQLite
      5. Save to history
      6. Return results as JSON
    """

    # ── Step 0: basic input check ─────────────────────────────────────────────
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if len(request.question) > 500:
        raise HTTPException(status_code=400, detail="Question too long (max 500 characters).")

    # ── Step 1: get schema ───────────────────────────────────────────────────
    schema = get_schema_description()

    # ── Step 2: call Gemini ───────────────────────────────────────────────────
    try:
        generated_sql = generate_sql(request.question, schema)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")

    # ── Step 3: handle CANNOT_ANSWER ─────────────────────────────────────────
    if "CANNOT_ANSWER" in generated_sql.upper():
        raise HTTPException(
            status_code=422,
            detail=(
                "The question cannot be answered with the current database schema. "
                "Try asking about employees, departments, or sales."
            ),
        )

    # ── Step 4: validate SQL ──────────────────────────────────────────────────
    is_safe, reason = validate_query(generated_sql)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Unsafe query blocked: {reason}")

    # ── Step 5: execute SQL ───────────────────────────────────────────────────
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(generated_sql)
        rows = cur.fetchall()
        conn.close()
        results = [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}. Generated SQL: {generated_sql}",
        )

    # ── Step 6: save to history ───────────────────────────────────────────────
    _save_history(request.question, generated_sql, len(results))

    return QueryResponse(
        question=request.question,
        generated_sql=generated_sql,
        results=results,
        row_count=len(results),
        executed_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    )


@app.get("/history", tags=["Database"])
def get_history(limit: int = 10):
    """
    Returns the last N queries made to this API.
    Default: last 10. Max: 50.
    """
    limit = min(limit, 50)
    _ensure_history_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM query_history ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return {
        "count": len(rows),
        "history": [dict(row) for row in rows],
    }


@app.delete("/history", tags=["Database"])
def clear_history():
    """Clears all query history records."""
    _ensure_history_table()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM query_history")
    conn.commit()
    conn.close()
    return {"message": "Query history cleared."}

# ── Feature 2: Query Explanation Endpoint ─────────────────────────────────────

class ExplainRequest(BaseModel):
    sql: str

    class Config:
        json_schema_extra = {
            "example": {
                "sql": "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3"
            }
        }


class ExplainResponse(BaseModel):
    sql: str
    explanation: str
    breakdown: dict


@app.post("/explain", response_model=ExplainResponse, tags=["Core"])
def explain_sql(request: ExplainRequest):
    """
    Takes any SQL query and returns:
    - Plain English explanation of what the query does
    - Breakdown of each SQL clause used
    
    Useful for non-technical users who receive SQL but cannot read it.
    """

    # ── Step 0: validate input ────────────────────────────────────────────────
    if not request.sql.strip():
        raise HTTPException(status_code=400, detail="SQL query cannot be empty.")

    if len(request.sql) > 2000:
        raise HTTPException(status_code=400, detail="SQL query too long (max 2000 characters).")

    # ── Step 1: build explanation prompt ──────────────────────────────────────
    explanation_prompt = f"""You are a SQL teacher explaining to a non-technical person.

Explain this SQL query in simple plain English:

SQL QUERY:
{request.sql}

RULES:
1. Write exactly 2-3 sentences.
2. No technical jargon. Use simple everyday words.
3. Start with "This query..."
4. Describe WHAT it does, not HOW SQL works internally.
5. Mention the table names and what data is being fetched.

EXPLANATION:"""

    # ── Step 2: build breakdown prompt ───────────────────────────────────────
    breakdown_prompt = f"""Analyze this SQL query and return a JSON object only.

SQL QUERY:
{request.sql}

Return ONLY a valid JSON object with these exact keys:
{{
  "tables_used": ["list of table names used"],
  "operation": "what type of operation (SELECT, JOIN, GROUP BY etc)",
  "filters": "what conditions or filters are applied (or 'None')",
  "sorting": "how results are sorted (or 'None')",
  "limit": "how many results are returned (or 'All')"
}}

Return ONLY the JSON. No explanation. No markdown. No backticks."""

    import requests as req
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY not found in .env file."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # ── Step 3: call Groq for plain English explanation ───────────────────────
    try:
        exp_response = req.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": explanation_prompt}],
                "temperature": 0.3,
                "max_tokens": 200
            },
            timeout=30
        )
        explanation = exp_response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM explanation error: {str(e)}")

    # ── Step 4: call Groq for structured breakdown ────────────────────────────
    try:
        breakdown_response = req.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": breakdown_prompt}],
                "temperature": 0.1,
                "max_tokens": 300
            },
            timeout=30
        )
        breakdown_raw = breakdown_response.json()["choices"][0]["message"]["content"].strip()

        # Clean any accidental markdown fences
        breakdown_raw = breakdown_raw.replace("```json", "").replace("```", "").strip()

        import json
        breakdown = json.loads(breakdown_raw)

    except Exception:
        # If JSON parsing fails, return a safe default
        breakdown = {
            "tables_used": [],
            "operation": "Could not parse",
            "filters": "Could not parse",
            "sorting": "Could not parse",
            "limit": "Could not parse"
        }

    return ExplainResponse(
        sql=request.sql,
        explanation=explanation,
        breakdown=breakdown
    )