from fastapi import FastAPI
from pydantic import BaseModel

from router import route_question
from sql_agent import generate_sql
from sql_executor import execute_sql

from retriever import retrieve_context
from rag_agent import answer_question

app = FastAPI(
    title="Healthcare RAG API"
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {
        "status": "running"
    }

@app.post("/chat")
def chat(request: ChatRequest):

    decision = route_question(request.message)

    if decision["route"] == "sql":
        sql = generate_sql(request.message)
        df = execute_sql(sql)

        return {
            "type": "table",
            "route": "sql",
            "sql": sql,
            "rows": df.to_dict(orient="records")
        }

    else:

        context = retrieve_context(request.message)
        answer = answer_question(
            request.message,
            context
        )

        return {
            "type": "text",
            "route": "rag",
            "answer": answer
        }