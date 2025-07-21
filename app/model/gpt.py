import backoff
from openai import OpenAI, RateLimitError

client = OpenAI()  # Automatically reads from your OPENAI_API_KEY

def build_prompt(schema: str, question: str) -> str:
    return f"""
# Context:
You are an AI assistant helping with querying a construction project database using SQL.

# Schema:
{schema}

# Request:
{question}

# SQL:
"""

@backoff.on_exception(backoff.expo, RateLimitError, max_tries=5)
def generate_sql(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",  # or "gpt-4.1"
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a data assistant for an electrical construction company. "
                    "Convert the user's request into an accurate SQL query based on the provided schema. "
                    "Be precise and use proper SQL syntax."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content
