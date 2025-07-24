# 🐬 NL2SQL — Talk to *any* SQL database in plain English


**NL2SQL** lets non‑technical users ask questions like “Which projects started in 2023?” and instantly see the SQL query **and** live results—no manual coding required.  
It runs **locally** (no OpenAI key) using Defog’s **[`sqlcoder‑7b‑2`](https://huggingface.co/defog/sqlcoder-7b-2)** language model.

---

## ✨ Features

* **Model‑powered SQL** – Generates accurate queries for filters, joins, aggregates, HAVING, etc.  
* **Works with any DB** – Pass any SQLAlchemy‑compatible connection string (PostgreSQL, MySQL, Snowflake, SQLite…).  
* **Runs on your GPU or CPU** – Uses `transformers`, `accelerate`, half‑precision offloading; tested on RTX 4070 Ti.  
* **Zero API cost** – All weights are cached locally via Hugging Face Hub.  
* **One‑file Docker deploy** – Spin it up on‑prem or in the cloud (Cloud Run, ECS, …).  
* **Extensible prompt** – Edit `app/model/llm.py` to add domain‑specific few‑shot examples.

---

## 🏗️ How it works

| Step | What happens | Tech |
|------|--------------|------|
| 1 | **Schema extractor** introspects the connected DB and builds a text schema. | SQLAlchemy |
| 2 | **Prompt builder** embeds that schema + Defog’s “Task / Schema / Answer” template. | Pydantic config |
| 3 | **SQLCoder‑7B‑2** (fine‑tuned Code‑LLaMA) generates candidate SQL. | 🤗 Transformers |
| 4 | We grab the **last** `SELECT …;` in the model output (ignoring earlier few‑shot examples). | Regex |
| 5 | (Optional) Run the query via SQLAlchemy and stream rows back to the UI. | SQLAlchemy |
| 6 | **Gradio UI** shows the raw SQL (syntax‑highlighted) and a results grid. | Gradio |

---

## 🚀 Quick start

```bash
# clone & enter
git clone https://github.com/anthonymercadante/nl2sql.git
cd nl2sql

# install python deps (GPU users: install torch+cu118/cu121 wheel manually)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# configure database & model
cp .env.example .env
# edit DATABASE_URL if needed

# launch local UI
python -m app.ui.interface
