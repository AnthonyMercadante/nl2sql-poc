from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from app.config import settings
import torch, re

# --------- load model & tokenizer -----------------
tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    settings.MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16,
    offload_folder="model_offload",
    trust_remote_code=False
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    do_sample=False,
    num_beams=settings.NUM_BEAMS,
    max_new_tokens=settings.MAX_TOKENS,
    pad_token_id=tokenizer.eos_token_id
)

# --------- prompt template ------------------------
def build_prompt(schema: str, question: str) -> str:
    return (
        "### Task\n"
        f"Generate a SQL query to answer [QUESTION]{question}[/QUESTION]\n\n"
        "### Database Schema\n"
        "The query will run on a database with the following schema:\n"
        f"{schema}\n\n"
        "### Answer\n"
        f"Given the database schema, here is the SQL query that "
        f"[QUESTION]{question}[/QUESTION]\n[SQL]\n"
    )

# --------- public helper --------------------------
def nl_to_sql(schema: str, question: str) -> str:
    prompt  = build_prompt(schema, question)
    raw     = pipe(prompt)[0]["generated_text"]

    # grab everything after [SQL] and before first semicolon
    sql_block = raw.split("[SQL]")[-1]
    sql_stmt  = re.search(r"SELECT.*?;", sql_block, re.IGNORECASE | re.DOTALL)
    return sql_stmt.group(0).strip() if sql_stmt else sql_block.strip()
