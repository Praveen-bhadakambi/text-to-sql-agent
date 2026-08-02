# Text-to-SQL Query Agent 🤖

> Convert plain English questions into SQL queries instantly using AI — powered by Groq LLaMA 3 and FastAPI.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-orange?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## What it does

Type a plain English question → AI generates SQL → executes on database → returns JSON results.

**Example:**
```
Question : "Who are the top 3 highest paid employees?"
Generated: SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3
Result   : [{"name": "Sneha Iyer", "salary": 98000}, ...]
```

---

## Live Demo

Start the server and visit the landing page:

```
http://localhost:8000/home   ← Project website
http://localhost:8000/docs   ← Interactive API explorer
```

---

## Features

- **Natural Language to SQL** — Ask questions in plain English, get SQL instantly
- **Schema Introspection** — Automatically reads all 6 database tables dynamically
- **SQL Safety Validator** — Blocks 8 dangerous operations (DROP, DELETE, UPDATE, etc.)
- **CSV Export** — Download query results as a CSV file
- **SQL Explanation** — Translates any SQL query into plain English
- **Rate Limiting** — 5 queries per IP per day (HTTP 429 on exceed)
- **Analytics Dashboard** — Usage stats, top keywords, active hours
- **Query History** — Stores all past queries with timestamps
- **Swagger UI** — Auto-generated interactive API docs at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| AI / LLM | Groq LLaMA 3.1 (llama-3.1-8b-instant) |
| Database | SQLite |
| Validation | Pydantic v2 |
| Security | Custom SQL safety validator |
| Language | Python 3.12 |

---

## Project Structure

```
text-to-sql-agent/
├── main.py               ← FastAPI app — all 9 endpoints
├── database.py           ← SQLite connection helper
├── schema_inspector.py   ← Reads DB schema dynamically for LLM prompt
├── sql_validator.py      ← Blocks unsafe SQL before execution
├── llm_service.py        ← Groq API integration (direct HTTP)
├── sample_data.py        ← Seeds company.db with 6 tables
├── static/
│   └── index.html        ← Project landing page
├── .env                  ← Your API key (never commit this)
├── .env.example          ← Template — safe to commit
├── requirements.txt      ← Python dependencies
└── README.md
```

---

## Database Schema (6 Tables)

```
departments  → id, name, budget
employees    → id, name, department_id (FK), salary, hire_date
sales        → id, employee_id (FK), amount, sale_date
products     → id, name, category, price, stock_qty
orders       → id, employee_id (FK), product_id (FK), quantity, order_date, status
attendance   → id, employee_id (FK), date, status
```

---

## API Endpoints (9 Total)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/schema` | View full live database schema |
| POST | `/query` | Convert NL question to SQL and execute |
| POST | `/query/limited` | Same with rate limiting (5/day per IP) |
| POST | `/export` | Download query results as CSV file |
| POST | `/explain` | Explain any SQL in plain English |
| GET | `/analytics` | Usage stats — queries, keywords, active hours |
| GET | `/history` | Last N queries with timestamps |
| DELETE | `/history` | Clear all query history |

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Praveen-bhadakambi/text-to-sql-agent.git
cd text-to-sql-agent
```

### 2. Create virtual environment

```bash
python -m venv venv

# Mac / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your free Groq API key

- Visit: https://console.groq.com
- Sign up free — no credit card needed
- Create API Key → copy it (starts with `gsk_...`)

### 5. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your key:
```
GROQ_API_KEY=gsk_your_real_key_here
```

### 6. Seed the database

```bash
python sample_data.py
```

Output:
```
✅ company.db seeded successfully.
   ├── departments  →  4 rows
   ├── employees    →  8 rows
   ├── sales        → 10 rows
   ├── products     →  5 rows
   ├── orders       →  6 rows
   └── attendance   →  8 rows
```

### 7. Start the server

```bash
uvicorn main:app --reload
```

### 8. Open in browser

```
http://localhost:8000/home    ← Landing page
http://localhost:8000/docs    ← Swagger API explorer
```

---

## Sample Questions to Try

```
Who are the top 3 highest paid employees?
How many employees are in each department?
What is the total sales amount per employee?
Which department has the highest budget?
Which product has the highest stock quantity?
How many orders were delivered in 2024?
Which employee placed the most orders?
List all employees who were absent on 2024-07-01.
What is the average salary in the Engineering department?
Which category has the most products?
```

---

## How It Works

```
User types plain English question
            ↓
POST /query  (FastAPI receives request)
            ↓
Schema Inspector reads all 6 tables dynamically
            ↓
Groq LLaMA 3 receives: question + schema → returns SQL
            ↓
SQL Validator: blocks DROP / DELETE / UPDATE / INSERT etc.
            ↓
SQLite executes the safe SELECT query
            ↓
Results saved to query_history table
            ↓
JSON response returned to user
```

---

## Security

- **SQL injection prevention** — Blocks 8 destructive operations with regex + comment stripping
- **Rate limiting** — 5 queries per IP per day, HTTP 429 on exceed
- **Read-only enforcement** — Only SELECT queries allowed
- **Input validation** — Pydantic v2 validates all request bodies
- **Key protection** — `.env` excluded from git via `.gitignore`

---

## Author

**Praveen Bhadakambi**
B.E. Computer Science & Engineering
Atria Institute of Technology, Bengaluru

- GitHub: [@Praveen-bhadakambi](https://github.com/Praveen-bhadakambi)
- LinkedIn: [linkedin.com/in/praveen-bhadakambi](https://linkedin.com/in/praveen-bhadakambi)
- Email: praveenbhadakambi@gmail.com

---

## License

This project is open source and available under the [MIT License](LICENSE).