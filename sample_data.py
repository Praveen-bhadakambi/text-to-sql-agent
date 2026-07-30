"""
Run this file to create and seed the company.db database.
Command: python sample_data.py
"""

import sqlite3

DB_PATH = "company.db"


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""

    -- ── Departments ───────────────────────────────────────────────────────────
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

    -- ── Products ──────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS products (
        id        INTEGER PRIMARY KEY,
        name      TEXT    NOT NULL,
        category  TEXT,
        price     REAL,
        stock_qty INTEGER
    );

    -- ── Orders ────────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS orders (
        id          INTEGER PRIMARY KEY,
        employee_id INTEGER,
        product_id  INTEGER,
        quantity    INTEGER,
        order_date  TEXT,
        status      TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (product_id)  REFERENCES products(id)
    );

    -- ── Attendance ────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS attendance (
        id          INTEGER PRIMARY KEY,
        employee_id INTEGER,
        date        TEXT,
        status      TEXT,
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

    -- ── Seed products ─────────────────────────────────────────────────────────
    INSERT OR IGNORE INTO products VALUES
        (1, 'Laptop',     'Electronics', 75000, 50),
        (2, 'Headphones', 'Electronics', 5000,  200),
        (3, 'Desk Chair', 'Furniture',   12000, 30),
        (4, 'Monitor',    'Electronics', 25000, 80),
        (5, 'Keyboard',   'Electronics', 3000,  150);

    -- ── Seed orders ───────────────────────────────────────────────────────────
    INSERT OR IGNORE INTO orders VALUES
        (1, 4, 1, 2, '2024-01-12', 'delivered'),
        (2, 5, 3, 1, '2024-01-18', 'delivered'),
        (3, 4, 2, 5, '2024-02-05', 'pending'),
        (4, 5, 4, 1, '2024-02-22', 'delivered'),
        (5, 8, 1, 1, '2024-03-08', 'cancelled'),
        (6, 4, 5, 3, '2024-03-20', 'delivered');

    -- ── Seed attendance ───────────────────────────────────────────────────────
    INSERT OR IGNORE INTO attendance VALUES
        (1,  1, '2024-07-01', 'present'),
        (2,  2, '2024-07-01', 'present'),
        (3,  3, '2024-07-01', 'absent'),
        (4,  4, '2024-07-01', 'present'),
        (5,  5, '2024-07-01', 'late'),
        (6,  1, '2024-07-02', 'present'),
        (7,  2, '2024-07-02', 'absent'),
        (8,  6, '2024-07-02', 'present');

    """)

    conn.commit()
    conn.close()

    print("✅ company.db seeded successfully.")
    print("")
    print("   Tables created:")
    print("   ├── departments  →  4 rows")
    print("   ├── employees    →  8 rows")
    print("   ├── sales        → 10 rows")
    print("   ├── products     →  5 rows")
    print("   ├── orders       →  6 rows")
    print("   └── attendance   →  8 rows")


if __name__ == "__main__":
    seed()