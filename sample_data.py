"""
Run this file ONCE to create and seed the company.db database.
Command: python sample_data.py
"""

import sqlite3

DB_PATH = "company.db"


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    -- ── Departments ──────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS departments (
        id     INTEGER PRIMARY KEY,
        name   TEXT    NOT NULL,
        budget REAL
    );

    -- ── Employees ─────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS employees (
        id            INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL,
        department_id INTEGER,
        salary        REAL,
        hire_date     TEXT,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    );

    -- ── Sales ─────────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS sales (
        id          INTEGER PRIMARY KEY,
        employee_id INTEGER,
        amount      REAL,
        sale_date   TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    );

    -- ── Seed departments ──────────────────────────────────────────────────────
    INSERT OR IGNORE INTO departments VALUES
        (1, 'Engineering', 500000),
        (2, 'Marketing',   300000),
        (3, 'Sales',       400000),
        (4, 'HR',          200000);

    -- ── Seed employees ────────────────────────────────────────────────────────
    INSERT OR IGNORE INTO employees VALUES
        (1, 'Priya Sharma',  1, 85000, '2022-03-15'),
        (2, 'Rahul Nair',    1, 92000, '2021-07-01'),
        (3, 'Ananya Bose',   2, 70000, '2023-01-10'),
        (4, 'Kiran Rao',     3, 75000, '2022-11-20'),
        (5, 'Deepa Menon',   3, 68000, '2023-05-05'),
        (6, 'Arjun Pillai',  4, 62000, '2023-08-12'),
        (7, 'Sneha Iyer',    1, 98000, '2020-04-01'),
        (8, 'Vikram Das',    2, 74000, '2022-06-18');

    -- ── Seed sales ────────────────────────────────────────────────────────────
    INSERT OR IGNORE INTO sales VALUES
        (1,  4, 15000, '2024-01-10'),
        (2,  5, 22000, '2024-01-15'),
        (3,  4, 18000, '2024-02-01'),
        (4,  5, 30000, '2024-02-20'),
        (5,  4, 12000, '2024-03-05'),
        (6,  5, 25000, '2024-03-18'),
        (7,  4, 19000, '2024-04-02'),
        (8,  5, 28000, '2024-04-20'),
        (9,  8, 11000, '2024-01-25'),
        (10, 8, 17000, '2024-03-10');
    """)

    conn.commit()
    conn.close()
    print("✅ company.db created and seeded successfully.")
    print("   Tables: departments, employees, sales")
    print("   Rows  : 4 departments | 8 employees | 10 sales")


if __name__ == "__main__":
    seed()
