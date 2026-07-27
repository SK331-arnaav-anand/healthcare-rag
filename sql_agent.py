from google import genai
from google.genai import types

client = genai.Client()

SQL_PROMPT = """
You are an expert PostgreSQL assistant.
Your task is to convert a user's healthcare question into a PostgreSQL SELECT query.

The only available table is:

patient_vectors

Schema:

id
patient_name
age
gender
blood_type
medical_condition
doctor
hospital
admission_type
admission_date
discharge_date
medication
test_results
insurance_provider
billing_amount
text


Rules:

1. ONLY generate SQL SELECT statements.
2. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE or CREATE.
3. Return raw SQL only. Never wrap it in markdown.
4. Use ILIKE for text matching.
5. Use LIMIT only if the user explicitly asks for a limited number of rows.
6. Never select the 'embedding','id', or 'text' column. Use explicit column names instead of SELECT *.
"""

def generate_sql(question):

    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=[
            SQL_PROMPT,
            question
        ],

        config=types.GenerateContentConfig(
            response_mime_type="text/plain"
        )

    )

    return response.text.strip()

# sql = generate_sql("Show everyone admitted after 2022")

# blocked = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]

# if any(word in sql for word in blocked):
#     raise Exception("Unsafe SQL generated.")

# print(sql)
