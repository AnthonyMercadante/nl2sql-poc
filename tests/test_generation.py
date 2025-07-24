def test_basic_select():
    from app.db.schema import extract_schema
    from app.model.llm  import nl_to_sql
    schema = "projects(id,name,start_date)"
    sql = nl_to_sql(schema, "List all projects")
    assert "SELECT" in sql and "FROM" in sql
