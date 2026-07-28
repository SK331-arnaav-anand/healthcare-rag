from google import genai
from google.genai import types
import json

client = genai.Client()

SYSTEM_PROMPT = """
You are a routing agent for a healthcare assistant.

Your only task is to decide whether a user's request should be answered by:

1. SQL
2. RAG

Return ONLY valid JSON.

Schema:

{
  "route": "sql" | "rag",
  "reason": "<one very short sentence>"
}

Use SQL if the question:

Asks for all records, filter patients, count, aggregate, averages, statistics, sorting,
tabular out, lists of patients, multiple records, or anything else that would be limited by 
the top k factor in a RAG pipeline.

Use RAG if the question:

- asks about one patient
- asks for an explanation
- asks for a summary
- asks "which", "why", "how"
- asks for natural-language answers
- asks about treatment history
- asks about one retrieved record

IMPORTANT: Do not answer the question. Return JSON only.
"""

def route_question(question):

    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[SYSTEM_PROMPT, question],
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
        )
    )

    return json.loads(response.text)


# test_questions = [
#     # SQL - filter
#     "Give me all patients with cancer and blood type B-",

#     # SQL - aggregation
#     "What is the average billing amount for diabetic patients?",

#     # SQL - count
#     "How many patients were admitted to Sons and Miller hospital?",

#     # RAG - single patient lookup
#     "Which hospital did Bobby Jackson get admitted to?",

#     # RAG - natural language reasoning
#     "Summarize the treatment history of John Terry."
# ]

# for q in test_questions:
#     result = route_question(q)   

#     print(result)