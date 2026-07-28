import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

POSTGRES = {
    "host": "healthcaredb.c94eay6ai7uu.ap-southeast-2.rds.amazonaws.com",
    "database": "postgres",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}


TOP_K = 5

_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    return _model


def retrieve_context(question):

    embedding = (
        get_model()
        .encode(
            question,
            normalize_embeddings=True,
        )
        .tolist()
    )

    conn = psycopg2.connect(**POSTGRES)
    register_vector(conn)

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            text,
            embedding <=> %s::vector AS distance
        FROM patient_vectors
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (
            embedding,
            embedding,
            TOP_K,
        ),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in rows]
