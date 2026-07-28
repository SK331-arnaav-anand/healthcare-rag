from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert healthcare assistant.

Answer ONLY using the provided patient records (context).

Use the conversation history only to resolve references such as:
- he / she / they
- that patient
- that hospital
- those patients
- now
- the previous one
and so on if it seemingly references a previous message. Do not use the conversation history as a source of facts. 

If the answer cannot be found in the retrieved context, say:
"I couldn't find that information in the patient records."
Do not make up information.
"""


def answer_question(question, contexts, history=None):

    if history is None:
        history = []

    context = "\n\n".join(contexts)

    conversation = ""

    for msg in history:
        role = msg.role if hasattr(msg, "role") else msg["role"]
        content = msg.content if hasattr(msg, "content") else msg["content"]
        conversation += f"{role.title()}: {content}\n"

    context_prompt = f"""
        Conversation History:

        {conversation}

        Retrieved Patient Information:

        {context}

        Current User Question:

        {question}
        """

    response = client.models.generate_content(

        model="gemini-2.5-flash",
        contents=[
            SYSTEM_PROMPT,
            context_prompt
        ]
    )

    tokens = response.usage_metadata.total_token_count

    return {
        "answer": response.text,
        "tokens": tokens
    }
