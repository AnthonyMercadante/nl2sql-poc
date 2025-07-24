from sqlalchemy import create_engine, inspect
from app.config import settings

def extract_schema() -> str:
    """Return a human‑readable schema description for the connected DB."""
    engine = create_engine(settings.DATABASE_URL)
    insp   = inspect(engine)

    lines = []
    for table in insp.get_table_names():
        cols = insp.get_columns(table)
        col_str = ", ".join(f"{c['name']} ({c['type']})" for c in cols)
        lines.append(f"Table: {table}\nColumns: {col_str}\n")
    return "\n".join(lines)
