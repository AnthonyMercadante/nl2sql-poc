from sqlalchemy import create_engine, inspect

def extract_schema(path="data/alectify.db"):
    engine = create_engine(f"sqlite:///{path}")
    inspector = inspect(engine)

    schema = ""
    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        col_str = ", ".join(f"{col['name']} ({col['type']})" for col in columns)
        schema += f"Table: {table}\nColumns: {col_str}\n\n"
    return schema
