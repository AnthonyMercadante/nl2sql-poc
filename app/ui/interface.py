import gradio as gr
from app.db.schema import extract_schema
from app.model.gpt import build_prompt, generate_sql

schema = extract_schema()

def handle_input(user_input):
    prompt = build_prompt(schema, user_input)
    return generate_sql(prompt)

def launch_ui():
    gr.Interface(fn=handle_input, inputs="text", outputs="text", title="Alectify NL2SQL Chatbot").launch()
