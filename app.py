from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from router import route_question
from sql_agent import generate_sql
from sql_executor import execute_sql

from retriever import retrieve_context
from rag_agent import answer_question

app = FastAPI(
    title="Healthcare RAG API"
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


@app.get("/")
def home():
    return {
        "status": "running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    history = request.history
    decision = route_question(request.message)

    if decision["route"] == "sql":

        sql_result = generate_sql(
            request.message,
            history
        )

        sql = sql_result["sql"]
        tokens = sql_result["tokens"]

        df = execute_sql(sql)

        return {
            "type": "table",
            "route": "sql",
            "sql": sql,
            "rows": df.to_dict(orient="records"),
            "token_usage": tokens
        }

    else:

        context = retrieve_context(request.message)

        answer_result = answer_question(
            request.message,
            context,
            history
        )

        return {
            "type": "text",
            "route": "rag",
            "answer": answer_result["answer"],
            "token_usage": answer_result["tokens"]
        }