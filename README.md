# Text-to-SQL Query Agent

A REST API that converts plain English questions into SQL queries using Google Gemini AI, executes them safely on a SQLite database, and returns structured JSON results.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| LLM | Google Gemini 1.5 Flash |
| Database | SQLite |
| Validation | Custom SQL safety validator |
| Environment | python-dotenv |

---

## Project Structure

```
text-to-sql-agent/
├── main.py               ← FastAPI app, all routes
├── database.py           ← SQLite connection helper
├── schema_inspector.py   ← Reads DB schema for LLM prompt
├── sql_validator.py      ← Blocks unsafe SQL before execution
├── llm_service.py        ← Gemini API integration
├── sample_data.py        ← Seeds company.db (run once)
├── .env                  ← Your API key (never commit this)
├── .env.example          ← Template — safe to commit
├── requirements.txt      ← Python dependencies
└── README.md             ← This file
```

---

## Setup Instructions

### 1. Clone / download the project

```bash
cd text-to-sql-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate it:
# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

```bash
cp .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your real key.
Get a free key at: https://aistudio.google.com/app/apikey

### 5. Seed the database (run once)

```bash
python sample_data.py
```

This creates `company.db` with 3 tables and sample data:
- `departments` — 4 rows
- `employees` — 8 rows
- `sales` — 10 rows

### 6. Start the server

```bash
uvicorn main:app --reload
```

Server runs at: http://localhost:8000
API Explorer at: http://localhost:8000/docs

---

## API Endpoints

### `GET /` — Health check
```json
{ "status": "running" }
```

### `GET /schema` — View database schema
Returns all table names and column definitions.

### `POST /query` — Main endpoint
**Request body:**
```json
{ "question": "Who are the top 3 highest paid employees?" }
```

**Response:**
```json
{
  "question": "Who are the top 3 highest paid employees?",
  "generated_sql": "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3",
  "results": [
    { "name": "Sneha Iyer", "salary": 98000 },
    { "name": "Rahul Nair", "salary": 92000 },
    { "name": "Priya Sharma", "salary": 85000 }
  ],
  "row_count": 3,
  "executed_at": "2024-07-11 10:30:00 UTC"
}
```

### `GET /history?limit=10` — Query history
Returns last N queries made to the API.

### `DELETE /history` — Clear history

---

## Sample Questions to Try

```
Who are the top 3 highest paid employees?
How many employees are in each department?
What is the total sales amount per employee?
Which department has the highest budget?
List all employees hired after 2022?
Who made the most sales in January 2024?
What is the average salary in the Engineering department?
```

---

## Resume Bullet Point

> Developed a Text-to-SQL REST API (FastAPI, Google Gemini API, SQLite) that converts natural language questions to validated SQL queries; implemented schema introspection, injection-safe validator blocking 8 dangerous SQL operations, query history logging, and deployed to Railway.

---

## How It Works (Flow)

```
User question (plain English)
        ↓
FastAPI POST /query
        ↓
Schema Inspector reads DB structure
        ↓
Gemini LLM receives: question + schema → returns SQL
        ↓
SQL Validator checks: SELECT only, no DROP/DELETE/etc.
        ↓
SQLite executes the query
        ↓
Results saved to query_history table
        ↓
JSON response returned to user
```
