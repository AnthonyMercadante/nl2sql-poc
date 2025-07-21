from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table, insert
from faker import Faker
import random

faker = Faker()
metadata = MetaData()

engine = create_engine("sqlite:///data/alectify.db")

# Alectify-relevant core tables
domains = {
    "projects": ["id", "name", "location", "start_date", "end_date"],
    "contractors": ["id", "company_name", "contact_name", "phone", "email"],
    "equipment": ["id", "project_id", "type", "manufacturer", "model", "cost"],
    "design_reviews": ["id", "project_id", "reviewer", "date", "status"],
    "materials": ["id", "name", "type", "unit_cost"],
    "site_visits": ["id", "project_id", "visitor", "date", "notes"],
    "energy_reports": ["id", "project_id", "score", "recommendations"],
    "documents": ["id", "project_id", "filename", "file_type", "uploaded_by"],
    "inspections": ["id", "project_id", "inspector", "result", "date"]
}

tables = {}

# Define schema
for name, cols in domains.items():
    table_cols = [Column("id", Integer, primary_key=True)]
    for col in cols[1:]:
        if "id" in col and col != "id":
            table_cols.append(Column(col, Integer))
        elif "date" in col:
            table_cols.append(Column(col, Date))
        elif "cost" in col or "score" in col:
            table_cols.append(Column(col, Float))
        else:
            table_cols.append(Column(col, String(255)))
    tables[name] = Table(name, metadata, *table_cols)

metadata.create_all(engine)

# Seed with realistic-looking fake data
with engine.begin() as conn:
    for i in range(25):  # Seed 25 rows per table
        conn.execute(insert(tables["projects"]), {
            "id": i + 1,
            "name": faker.bs().title(),
            "location": faker.city(),
            "start_date": faker.date_between(start_date='-2y', end_date='-1y'),
            "end_date": faker.date_between(start_date='-1y', end_date='today')
        })

        conn.execute(insert(tables["contractors"]), {
            "id": i + 1,
            "company_name": faker.company(),
            "contact_name": faker.name(),
            "phone": faker.phone_number(),
            "email": faker.company_email()
        })

        conn.execute(insert(tables["equipment"]), {
            "id": i + 1,
            "project_id": random.randint(1, 25),
            "type": random.choice(["Panel", "Cable", "Breaker", "Transformer"]),
            "manufacturer": faker.company(),
            "model": faker.bothify(text="EQ-####"),
            "cost": round(random.uniform(1000, 10000), 2)
        })

        conn.execute(insert(tables["design_reviews"]), {
            "id": i + 1,
            "project_id": random.randint(1, 25),
            "reviewer": faker.name(),
            "date": faker.date_between(start_date='-1y', end_date='today'),
            "status": random.choice(["approved", "changes requested", "pending"])
        })

        conn.execute(insert(tables["materials"]), {
            "id": i + 1,
            "name": random.choice(["Conduit", "Wire", "Pipe", "Mount"]),
            "type": random.choice(["Copper", "Plastic", "Steel"]),
            "unit_cost": round(random.uniform(10, 100), 2)
        })

        conn.execute(insert(tables["site_visits"]), {
            "id": i + 1,
            "project_id": random.randint(1, 25),
            "visitor": faker.name(),
            "date": faker.date_between(start_date='-1y', end_date='today'),
            "notes": faker.sentence()
        })

        conn.execute(insert(tables["energy_reports"]), {
            "id": i + 1,
            "project_id": random.randint(1, 25),
            "score": round(random.uniform(0.5, 1.0), 2),
            "recommendations": faker.sentence()
        })

        conn.execute(insert(tables["documents"]), {
            "id": i + 1,
            "project_id": random.randint(1, 25),
            "filename": faker.file_name(),
            "file_type": random.choice(["pdf", "dwg", "txt"]),
            "uploaded_by": faker.name()
        })

        conn.execute(insert(tables["inspections"]), {
            "id": i + 1,
            "project_id": random.randint(1, 25),
            "inspector": faker.name(),
            "result": random.choice(["pass", "fail", "pending"]),
            "date": faker.date_between(start_date='-1y', end_date='today')
        })

print("✅ Seeded alectify.db with schema and data in /data/alectify.db")
