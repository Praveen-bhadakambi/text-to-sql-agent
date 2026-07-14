"""
LLM Service — Groq API (Free, no credit card needed)
──────────────────────────────────────────────────────
Uses LLaMA 3 model via Groq's free API.
Get your free key at: https://console.groq.com
.env must contain: GROQ_API_KEY=gsk_...
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

_PROMPT_TEMPLATE = """You are an expert SQLite SQL writer.

Given the DATABASE SCHEMA below, convert the USER QUESTION into a valid SQLite SELECT query.

DATABASE SCHEMA:
{schema}

STRICT RULES:
1. Return ONLY the raw SQL query. No explanation. No markdown. No backticks. No comments.
2. Use ONLY SELECT statements. Never write DROP, DELETE, INSERT, UPDATE or ALTER.
3. Use exact table names and column names from the schema above.
4. For questions involving names across tables, use JOIN with the foreign key shown.
5. If the question cannot be answered with the given schema, return exactly: CANNOT_ANSWER
6. If the question is ambiguous, make a reasonable assumption and write the query.

USER QUESTION: {question}

SQL QUERY:"""


def generate_sql(natural_language: str, schema: str) -> str:
    """
    Calls Groq API and returns a SQL query string.

    Args:
        natural_language : user's plain-English question
        schema           : DB schema string from schema_inspector

    Returns:
        Raw SQL string, or "CANNOT_ANSWER"
    """

    # ── Guard: key must exist ─────────────────────────────────────────────────
    if not GROQ_API_KEY:
        raise Exception(
            "GROQ_API_KEY is missing. "
            "Get a free key at https://console.groq.com and "
            "add it to .env: GROQ_API_KEY=gsk_..."
        )

    if not GROQ_API_KEY.startswith("gsk_"):
        raise Exception(
            f"GROQ_API_KEY looks wrong (got: {GROQ_API_KEY[:10]}...). "
            "It must start with 'gsk_'. Get a fresh key at https://console.groq.com"
        )

    # ── Build prompt ──────────────────────────────────────────────────────────
    prompt = _PROMPT_TEMPLATE.format(
        schema=schema,
        question=natural_language.strip()
    )

    # ── Call Groq API ─────────────────────────────────────────────────────────
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.1-8b-instant",   # free model, very fast
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 512,
    }

    try:
        response = requests.post(
            url=GROQ_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.exceptions.ConnectionError:
        raise Exception("Network error: cannot reach Groq API. Check your internet.")
    except requests.exceptions.Timeout:
        raise Exception("Groq API timed out after 30 seconds. Try again.")

    # ── Handle HTTP errors ────────────────────────────────────────────────────
    if response.status_code == 401:
        raise Exception(
            "Invalid Groq API key (401). "
            "Get a fresh key at https://console.groq.com"
        )
    if response.status_code == 429:
        raise Exception("Groq rate limit hit. Wait a moment and try again.")
    if response.status_code != 200:
        raise Exception(
            f"Groq API returned HTTP {response.status_code}: {response.text[:200]}"
        )

    # ── Parse response ────────────────────────────────────────────────────────
    try:
        data = response.json()
        sql = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        raise Exception(
            f"Unexpected Groq response format: {str(e)} | raw: {response.text[:300]}"
        )

    # ── Clean up any accidental markdown fences ───────────────────────────────
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql


# ── Quick self-test: python llm_service.py ────────────────────────────────────
if __name__ == "__main__":
    from schema_inspector import get_schema_description

    print("Testing Groq API connection...\n")

    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in .env")
        print("   Add: GROQ_API_KEY=gsk_... to your .env file")
    elif not GROQ_API_KEY.startswith("gsk_"):
        print(f"❌ Key looks wrong: {GROQ_API_KEY[:10]}... (must start with gsk_)")
    else:
        print(f"✅ Key found: {GROQ_API_KEY[:10]}...")
        try:
            schema = get_schema_description()
            result = generate_sql("List all employees", schema)
            print(f"✅ Groq responded successfully")
            print(f"   Generated SQL: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
