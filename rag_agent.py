from google import genai
client = genai.Client()

SYSTEM_PROMPT = """
You are an expert healthcare assistant.

Answer ONLY using the provided context.

Do not make up information. If the answer cannot be found in the context, 
say: 'I couldn't find that information in the patient records.'
"""


def answer_question(question, contexts):

    context = "\n\n".join(contexts)

    prompt = f"""
Context:

{context}

Question:

{question}
"""

    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=[
            SYSTEM_PROMPT,
            prompt
        ]

    )

    return response.text