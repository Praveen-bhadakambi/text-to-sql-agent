"""
Schema Inspector
────────────────
Reads the live SQLite database and returns a human-readable schema
description that is injected into the LLM prompt.

Why this matters:
  The LLM has no idea what tables or columns exist in your DB.
  By passing the schema in the prompt, the LLM can generate accurate SQL.
"""

from database import get_connection


def get_schema_description() -> str:
    """
    Returns a plain-text description of all tables and their columns.

    Example output:
        Table 'employees': id (INTEGER), name (TEXT), salary (REAL), ...
        Table 'departments': id (INTEGER), name (TEXT), budget (REAL)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Get all user-created table names (exclude sqlite internal tables)
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND name NOT LIKE 'sqlite_%'
          AND name != 'query_history'
        ORDER BY name;
    """)
    tables = [row[0] for row in cur.fetchall()]

    if not tables:
        conn.close()
        return "No tables found in database."

    schema_lines = []
    for table in tables:
        cur.execute(f"PRAGMA table_info({table});")
        columns = cur.fetchall()
        # Each column row: (cid, name, type, notnull, dflt_value, pk)
        col_defs = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        schema_lines.append(f"Table '{table}': {col_defs}")

        # Also show foreign keys so LLM can write JOINs
        cur.execute(f"PRAGMA foreign_key_list({table});")
        fks = cur.fetchall()
        for fk in fks:
            schema_lines.append(
                f"  → '{table}'.{fk[3]} references '{fk[2]}'.{fk[4]}"
            )

    conn.close()
    return "\n".join(schema_lines)


if __name__ == "__main__":
    # Quick test — run: python schema_inspector.py
    print(get_schema_description())
