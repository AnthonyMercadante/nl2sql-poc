from transformers import pipeline

# Load the local model
pipe = pipeline("text2text-generation", model="defog/sqlcoder", device_map="auto")

def build_prompt(schema: str, question: str) -> str:
    return f"""\
# Context:
You are an AI assistant that converts user questions into SQL queries for a construction and engineering database.

# Schema:
{schema}

# Question:
{question}

# SQL:
"""

def generate_sql(prompt: str) -> str:
    result = pipe(prompt, max_length=256)[0]['generated_text']
    return result.strip()
