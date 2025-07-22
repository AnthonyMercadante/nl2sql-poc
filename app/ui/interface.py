import gradio as gr
from app.db.schema import extract_schema
from app.model.local_model import build_prompt, generate_sql, execute_sql_query

schema = extract_schema()

def handle_input(user_text):
    prompt = build_prompt(schema, user_text)
    sql    = generate_sql(prompt)
    hdrs, rows = execute_sql_query(sql)
    return sql, gr.Dataframe(headers=hdrs, value=rows)

def launch_ui():
    gr.Interface(
        fn       = handle_input,
        inputs   = gr.Textbox(lines=2, placeholder="Ask in plain English…"),
        outputs  = [gr.Textbox(label="Generated SQL"),
                    gr.Dataframe(label="Query Results")],
        title    = "NL2SQL Chatbot"
    ).launch()
