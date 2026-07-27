import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="Healthcare RAG",
    layout="wide"
)

st.title("Healthcare RAG Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "table":
            st.dataframe(message["content"], use_container_width=True)

prompt = st.chat_input("Ask me anything about the healthcare dataset!")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "type": "text",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):

        response = requests.post(
            API_URL,
            json={
                "message": prompt
            }
        )

        result = response.json()

    with st.chat_message("assistant"):

        if result["type"] == "text":

            st.markdown(result["answer"])

            st.session_state.messages.append({
                "role": "assistant",
                "type": "text",
                "content": result["answer"]
            })

        else:

            st.code(result["sql"], language="sql")

            st.dataframe(result["rows"], use_container_width=True)

            st.session_state.messages.append({
                "role": "assistant",
                "type": "table",
                "content": result["rows"]
            })
