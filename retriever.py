import psycopg2
from pgvector.psycopg2 import register_vector
import os
import requests

POSTGRES = {
    "host": "healthcaredb.c94eay6ai7uu.ap-southeast-2.rds.amazonaws.com",
    "database": "postgres",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = (
    "https://router.huggingface.co/"
    "hf-inference/models/"
    "sentence-transformers/all-MiniLM-L6-v2/"
    "pipeline/feature-extraction"
)

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

TOP_K = 5


def get_embedding(text: str):

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={
            "inputs": text
        },
        timeout=30,
    )

    response.raise_for_status()

    embedding = response.json()

    # HF returns [[...]] for a single input
    return embedding[0]


def retrieve_context(question):

    embedding = get_embedding(question)

    conn = psycopg2.connect(**POSTGRES)
    register_vector(conn)

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            text
        FROM patient_vectors
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (
            embedding,
            TOP_K,
        ),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in rows]
