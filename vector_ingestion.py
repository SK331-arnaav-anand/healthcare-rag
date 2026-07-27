import boto3
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer


BUCKET_NAME = "healthcare-sandbox"
S3_PATH = "healthcare_dataset_cleaned.csv"

POSTGRES = {
    "host": "healthcaredb.c94eay6ai7uu.ap-southeast-2.rds.amazonaws.com",
    "database": "postgres",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

BATCH_SIZE = 500

s3 = boto3.client("s3")

obj = s3.get_object(
    Bucket=BUCKET_NAME,
    Key=S3_PATH
)

df = pd.read_csv(obj["Body"])

for col in ["Date of Admission", "Discharge Date"]:
    df[col] = pd.to_datetime(
        df[col],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

print("Loading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(**POSTGRES)

register_vector(conn)

cur = conn.cursor()

insert_sql = """
INSERT INTO patient_vectors (

    id,

    patient_name,
    age,
    gender,

    blood_type,
    medical_condition,

    doctor,
    hospital,

    admission_type,
    admission_date,
    discharge_date,

    medication,
    test_results,

    insurance_provider,
    billing_amount,

    text,

    embedding

)
VALUES %s
"""

rows = []

print("Preparing patient documents...")

for idx, row in df.iterrows():

    paragraph = (
        f"{row['Name']} is a {row['Age']}-year-old "
        f"{row['Gender'].lower()} with blood type {row['Blood Type']}. "
        f"They were admitted to {row['Hospital']} on "
        f"{row['Date of Admission'].strftime('%d %B %Y')} "
        f"under {row['Admission Type'].lower()} admission "
        f"for treatment of {row['Medical Condition'].lower()}. "
        f"The attending physician was Dr. {row['Doctor']}. "
        f"They stayed in room {row['Room Number']} and received "
        f"{row['Medication']}. "
        f"They were discharged on "
        f"{row['Discharge Date'].strftime('%d %B %Y')} "
        f"with {row['Test Results'].lower()} test results. "
        f"Their treatment was covered by "
        f"{row['Insurance Provider']} "
        f"and the total billing amount was "
        f"£{row['Billing Amount']:.2f}."
    )

    rows.append((idx, row, paragraph))


print("Generating embeddings and inserting into PostgreSQL...")

for start in range(0, len(rows), BATCH_SIZE):

    batch = rows[start:start+BATCH_SIZE]

    texts = [r[2] for r in batch]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    values = []

    for (idx, row, paragraph), embedding in zip(batch, embeddings):

        values.append(

            (

                int(idx),

                row["Name"],
                int(row["Age"]),
                row["Gender"],

                row["Blood Type"],
                row["Medical Condition"],

                row["Doctor"],
                row["Hospital"],

                row["Admission Type"],
                row["Date of Admission"],
                row["Discharge Date"],

                row["Medication"],
                row["Test Results"],

                row["Insurance Provider"],
                float(row["Billing Amount"]),

                paragraph,

                embedding.tolist()

            )

        )

    execute_values(
        cur,
        insert_sql,
        values
    )

    conn.commit()

    print(
        f"Inserted {min(start+BATCH_SIZE, len(rows)):,} / {len(rows):,}"
    )

cur.close()
conn.close()

print("====================================")
print("Ingestion completed successfully!")
print(f"Total records: {len(df):,}")
print("====================================")