# --- imports & paths stay the same ---
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch, sqlite3, os, re

MODEL_NAME = "defog/sqlcoder-7b-2"         # <— new model name

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    offload_folder="model_offload",
    torch_dtype=torch.float16,
    trust_remote_code=False
)

# pipeline now uses num_beams=4 for better accuracy
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    do_sample=False,
    num_beams=4,
    max_new_tokens=256,
    pad_token_id=tokenizer.eos_token_id
)

def build_prompt(schema: str, question: str) -> str:
    return f"""### Task
    Generate a SQL query to answer [QUESTION]{question}[/QUESTION]

    ### Database Schema
    The query will run on a database with the following schema:
    {schema}

    ### Answer
    Given the database schema, here is the SQL query that [QUESTION]{question}[/QUESTION]
    [SQL]
    """


def generate_sql(prompt: str) -> str:
    """
    Return the LAST complete SELECT‑statement the model produces.
    """
    raw = pipe(prompt, max_new_tokens=256, do_sample=False)[0]["generated_text"]

    # Find all occurrences of SELECT … ;  (non‑greedy)
    candidates = re.findall(r"SELECT.*?;", raw, flags=re.IGNORECASE | re.DOTALL)

    if not candidates:
        return raw.strip()                      # fallback: return everything

    sql = candidates[-1]                       # take the last one (our answer)
    return sql.strip()


# ---------- cleaners ---------- #
def clean_sql(text: str) -> str:
    text = re.sub(r"```(?:sql)?", "", text)      # remove fenced code blocks
    text = re.sub(r"#.*", "", text)              # remove inline comments
    return text.strip().rstrip(";") + ";"        # ensure exactly one trailing ;

# ---------- DB helper ---------- #
def execute_sql_query(sql: str, db_path="data/alectify.db"):
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        headers = [d[0] for d in cur.description]
        return headers, rows
    except Exception as e:
        return ["Error"], [[str(e)]]
    finally:
        conn.close()
