from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SQL_PROMPT = """
You are an expert PostgreSQL assistant.

Your task is to convert a user's healthcare question into a PostgreSQL SELECT query.

The only available table is: patient_vectors

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
6. Never select the 'embedding', 'id', or 'text' column. Use explicit column names instead of SELECT *.
7. If the current question seems to refer to previous conversations (e.g. "he", "she", "they", "those", "that hospital", "now only the females"), use the conversation history to infer the intended meaning before generating the SQL.
"""


def generate_sql(question, history=None):

    if history is None:
        history = []

    conversation = ""

    for msg in history:
        role = msg.role if hasattr(msg, "role") else msg["role"]
        content = msg.content if hasattr(msg, "content") else msg["content"]
        conversation += f"{role.title()}: {content}\n"

    context_prompt = f"""
        Conversation History:
        {conversation}

        Current User Question:
        {question}
        """

    response = client.models.generate_content(

        model="gemini-2.5-flash",
        contents=[
            SQL_PROMPT,
            context_prompt
        ],

        config=types.GenerateContentConfig(
            response_mime_type="text/plain"
        )

    )

    tokens = response.usage_metadata.total_token_count

    return {
        "sql": response.text.strip(),
        "tokens": tokens
    }
