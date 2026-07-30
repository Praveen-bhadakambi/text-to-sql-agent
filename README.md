# Text-to-SQL Query Agent

An AI-powered REST API that converts plain English questions into SQL queries using Groq LLaMA 3, executes them safely on a SQLite database, and returns structured JSON results.

---

## Live Demo

> Start the server and visit: `http://localhost:8000/docs`

**Example:**
- Input: `"Who are the top 3 highest paid employees?"`
- Output: Automatically generates and executes the correct SQL → returns JSON results

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| AI / LLM | Groq LLaMA 3.1 (llama-3.1-8b-instant) |
| Database | SQLite |
| Validation | Custom SQL safety validator |
| Data Export | CSV via StreamingResponse |
| Environment | python-dotenv |
| Language | Python 3.12 |

---

## Project Structure

text-to-sql-agent/
├── main.py ← FastAPI app — all 9 endpoints
├── database.py ← SQLite connection helper
├── schema_inspector.py ← Reads DB schema dynamically for LLM prompt
├── sql_validator.py ← Blocks unsafe SQL before execution
├── llm_service.py ← Groq API integration
├── sample_data.py ← Seeds company.db with 6 tables (run once)
├── .env ← Your API key (never commit this)
├── .env.example ← Template — safe to commit
├── requirements.txt ← Python dependencies
└── README.md ← This file


---

## Database Schema (6 Tables)

departments → id, name, budget
employees → id, name, department_id, salary, hire_date
sales → id, employee_id, amount, sale_date
products → id, name, category, price, stock_qty
orders → id, employee_id, product_id, quantity, order_date, status
attendance → id, employee_id, date, status


**Relationships:**
- `employees.department_id` → `departments.id`
- `sales.employee_id` → `employees.id`
- `orders.employee_id` → `employees.id`
- `orders.product_id` → `products.id`
- `attendance.employee_id` → `employees.id`

---

## API Endpoints (9 Total)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/schema` | View full database schema |
| POST | `/query` | Convert NL question to SQL and execute |
| POST | `/query/limited` | Same as /query with rate limiting (5/day per IP) |
| POST | `/export` | Run query and download results as CSV |
| POST | `/explain` | Explain any SQL query in plain English |
| GET | `/analytics` | Usage stats — total queries, top keywords, active hours |
| GET | `/history` | Last N queries made to the API |
| DELETE | `/history` | Clear all query history |

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Praveen-bhadakambi/text-to-sql-agent.git
cd text-to-sql-agent
```

### 2. Create a virtual environment

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
- Sign up free (no credit card)
- Create API key → copy it

### 5. Add your API key

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder:

GROQ_API_KEY=gsk_your_real_key_here


### 6. Seed the database (run once)

```bash
python sample_data.py
```

Output:

✅ company.db seeded successfully.
├── departments → 4 rows
├── employees → 8 rows
├── sales → 10 rows
├── products → 5 rows
├── orders → 6 rows
└── attendance → 8 rows


### 7. Start the server

```bash
uvicorn main:app --reload
```

Visit: http://localhost:8000/docs

---

## Sample Questions to Try

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


---

## How It Works

User types plain English question
↓
POST /query (FastAPI)
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


---

## Security Features

- SQL injection prevention — blocks 8 destructive operations
- Rate limiting — 5 queries per IP per day (HTTP 429 on exceed)
- Read-only enforcement — only SELECT queries allowed
- Comment stripping — removes SQL comments before validation

---

## Resume Bullet Points

> Engineered an AI-powered Text-to-SQL REST API (FastAPI, Groq LLaMA 3, SQLite, Python) with 9 endpoints converting natural language to validated SQL; implemented schema introspection across 6 relational tables, CSV export, SQL explanation, rate limiting (5 req/day), and usage analytics dashboard.

---

## Author

**Praveen Bhadakambi**
- GitHub: [@Praveen-bhadakambi](https://github.com/Praveen-bhadakambi)
- LinkedIn: [linkedin.com/in/praveen-bhadakambi](https://linkedin.com/in/praveen-bhadakambi)