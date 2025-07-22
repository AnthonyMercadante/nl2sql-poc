from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch, sqlite3, os, re

# ---------- model ---------- #
os.makedirs("model_offload", exist_ok=True)

tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder")

model = AutoModelForCausalLM.from_pretrained(
    "defog/sqlcoder",
    device_map="auto",
    offload_folder="model_offload",
    torch_dtype=torch.float16,   # lower VRAM use
    trust_remote_code=False      # safer load
)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# ---------- prompting ---------- #
FEW_SHOT = """
-- Example 1  (simple filter on date)
-- Question: List all projects that started in 2022.
SELECT name
FROM projects
WHERE start_date BETWEEN '2022-01-01' AND '2022-12-31';

-- Example 2  (aggregation on one table)
-- Question: Show the total cost of all equipment used in project ID 7.
SELECT SUM(cost) AS total_cost
FROM equipment
WHERE project_id = 7;

-- Example 3  (plain SELECT no WHERE)
-- Question: Get names and emails of all contractors.
SELECT company_name, email
FROM contractors;

-- Example 4  (filter on text column)
-- Question: Find all documents uploaded by 'John Smith'.
SELECT *
FROM documents
WHERE uploaded_by = 'John Smith';

-- Example 5  (count with date filter)
-- Question: How many inspections failed in 2023?
SELECT COUNT(*) AS failed_count
FROM inspections
WHERE result = 'fail'
  AND date BETWEEN '2023-01-01' AND '2023-12-31';

-- Example 6  (ORDER BY DESC LIMIT 1)
-- Question: Which project had the highest energy score?
SELECT p.name, e.score
FROM projects p
JOIN energy_reports e USING (project_id)
ORDER BY e.score DESC
LIMIT 1;

-- Example 7  (GROUP BY COUNT)
-- Question: Get the number of site visits per project.
SELECT project_id, COUNT(*) AS visits
FROM site_visits
GROUP BY project_id;

-- Example 8  (JOIN with location filter)
-- Question: List all equipment used in projects located in Toronto.
SELECT e.*
FROM equipment e
JOIN projects p ON p.id = e.project_id
WHERE p.location = 'Toronto';

-- Example 9  (AVG with GROUP BY)
-- Question: What’s the average unit cost of each material type?
SELECT type, AVG(unit_cost) AS avg_cost
FROM materials
GROUP BY type;

-- Example 10 (latest by date per project)
-- Question: Show the latest design review status for each project.
SELECT d.project_id,
       d.status
FROM design_reviews d
JOIN (
      SELECT project_id, MAX(date) AS max_date
      FROM design_reviews
      GROUP BY project_id
) x USING (project_id, date);

-- Example 11 (HAVING with join & count)
-- Question: List all projects with more than 5 site visits and a failed inspection.
SELECT p.name
FROM projects p
JOIN site_visits v ON v.project_id = p.id
JOIN inspections  i ON i.project_id = p.id
WHERE i.result = 'fail'
GROUP BY p.name
HAVING COUNT(v.id) > 5;

-- Example 12 (join-many with filter on SUM)
-- Question: Which contractors worked on projects that had equipment costing over $100,000?
SELECT DISTINCT c.company_name
FROM contractors c
JOIN projects    p ON p.id = c.id         -- adjust if you have a junction table
JOIN equipment   e ON e.project_id = p.id
GROUP BY c.company_name
HAVING SUM(e.cost) > 100000;

-- Example 13 (multi‑measure select)
-- Question: For each project, show the total material cost and energy report score.
SELECT p.id,
       SUM(m.unit_cost) AS total_material_cost,
       AVG(er.score)    AS avg_energy_score
FROM projects p
LEFT JOIN materials      m ON m.id = p.id          -- sample join
LEFT JOIN energy_reports er ON er.project_id = p.id
GROUP BY p.id;

-- Example 14 (double filter)
-- Question: List projects where the design review status is 'rejected'
--           and inspection result is 'fail'.
SELECT DISTINCT p.name
FROM projects p
JOIN design_reviews d ON d.project_id = p.id AND d.status = 'rejected'
JOIN inspections    i ON i.project_id = p.id AND i.result = 'fail';

-- Example 15 (group & sum per project)
-- Question: Show a summary of all equipment types used by project,
--           including total count and cost.
SELECT project_id,
       type,
       COUNT(*) AS item_count,
       SUM(cost) AS total_cost
FROM equipment
GROUP BY project_id, type;
"""


def build_prompt(schema: str, question: str) -> str:
    return (
        f"{FEW_SHOT}\n"
        f"-- Now answer the next question using the same SQL style.\n"
        f"-- Schema (for reference):\n{schema}\n"
        f"-- Question: {question}\n"
        f"-- SQL\n"
    )


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
