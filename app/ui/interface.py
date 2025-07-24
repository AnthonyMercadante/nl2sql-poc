import gradio as gr
from app.db.schema import extract_schema
from app.model.llm     import nl_to_sql
from app.config        import settings
from sqlalchemy        import create_engine, text

schema = extract_schema()
engine = create_engine(settings.DATABASE_URL)

def handle_query(question: str):
    sql = nl_to_sql(schema, question)
    # run the SQL and fetch rows
    try:
        with engine.begin() as conn:
            rows = [tuple(r) for r in conn.execute(text(sql))]
            headers = rows[0].keys() if rows else []
            rows    = [tuple(r) for r in rows]
    except Exception as exc:
        headers, rows = ["Error"], [[str(exc)]]
    return sql, gr.Dataframe(headers=headers, value=rows)

def launch_ui():
    gr.Interface(
        fn        = handle_query,
        inputs    = gr.Textbox(lines=2, label="Ask in plain English…"),
        outputs   = [
            gr.Code(label="Generated SQL", language="sql"),
            gr.Dataframe(label="Query Results")
        ],
        title     = "NL2SQL Chatbot"
    ).launch()

if __name__ == "__main__":
    launch_ui()
