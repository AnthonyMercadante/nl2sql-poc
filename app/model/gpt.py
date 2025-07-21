import openai

def build_prompt(schema, question):
    return f"""
Schema:
{schema}

Instruction:
Translate the following request into SQL.

Request:
{question}

SQL:
"""

def generate_sql(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response['choices'][0]['message']['content']
