import psycopg2
import pandas as pd

POSTGRES = {
    "host": "healthcaredb.c94eay6ai7uu.ap-southeast-2.rds.amazonaws.com",
    "database": "postgres",      
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}


def validate_sql(sql: str):
    sql = sql.strip()
    if not sql.upper().startswith("SELECT"):
        raise Exception("Only SELECT statements are allowed.")
    return sql


def execute_sql(sql: str):
    validate_sql(sql)
    conn = psycopg2.connect(**POSTGRES)
    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()

    return df