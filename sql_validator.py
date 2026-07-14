"""
SQL Safety Validator
─────────────────────
Before executing any LLM-generated SQL, this module checks that:
  1. The query starts with SELECT (read-only)
  2. No destructive keywords are present (DROP, DELETE, etc.)
  3. No SQL comment tricks are used to hide injections
  4. Query length is reasonable

This is a critical security layer — never skip it.
"""

import re


# Any SQL keyword that can modify or destroy data
BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "INSERT",
    "UPDATE", "CREATE", "REPLACE", "ATTACH", "DETACH",
    "PRAGMA", "VACUUM",
]


def validate_query(sql: str) -> tuple[bool, str]:
    """
    Validates an LLM-generated SQL query before execution.

    Args:
        sql: The raw SQL string from the LLM.

    Returns:
        (True, "OK")          — safe to execute
        (False, reason_str)   — blocked, reason explains why

    Example:
        is_safe, reason = validate_query("SELECT * FROM employees")
        # → (True, "OK")

        is_safe, reason = validate_query("DROP TABLE employees")
        # → (False, "Query blocked: 'DROP' operations are not allowed.")
    """

    if not sql or not sql.strip():
        return False, "Empty query received from LLM."

    # Strip SQL comments (-- line comments and /* block comments */)
    # Attackers sometimes hide keywords inside comments
    cleaned = re.sub(r'--[^\n]*', '', sql)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
    cleaned_upper = cleaned.upper().strip()

    # Rule 1: Must start with SELECT
    if not cleaned_upper.startswith("SELECT"):
        return False, (
            "Only SELECT queries are allowed. "
            f"Your query starts with: '{sql.strip()[:30]}...'"
        )

    # Rule 2: No destructive keywords
    for keyword in BLOCKED_KEYWORDS:
        pattern = rf'\b{keyword}\b'
        if re.search(pattern, cleaned_upper):
            return False, f"Query blocked: '{keyword}' operations are not allowed."

    # Rule 3: Reasonable length (SQLite has no hard limit but LLMs can hallucinate huge queries)
    if len(sql) > 2000:
        return False, "Query is unusually long. Please try a simpler question."

    return True, "OK"


if __name__ == "__main__":
    # Quick self-test
    test_cases = [
        ("SELECT * FROM employees", True),
        ("DROP TABLE employees", False),
        ("SELECT * FROM employees; DELETE FROM employees", False),
        ("-- DROP TABLE\nSELECT 1", True),
        ("UPDATE employees SET salary=0", False),
        ("select name from employees where salary > 80000", True),
    ]

    print("SQL Validator — self-test\n")
    for sql, expected_safe in test_cases:
        ok, msg = validate_query(sql)
        status = "✅ PASS" if (ok == expected_safe) else "❌ FAIL"
        print(f"{status} | safe={ok} | {sql[:50]}")
        if not ok:
            print(f"       reason: {msg}")
