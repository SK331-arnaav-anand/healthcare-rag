import time
import requests
import pandas as pd
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="Healthcare RAG Assistant",
    layout="wide"
)


with st.sidebar:
    st.title("Healthcare RAG")
    st.markdown("---")

    st.markdown("### Architecture")
    st.write("LLM: Gemini 2.5 Flash")
    st.write("Embeddings: MiniLM-L6-v2")
    st.write("Vector DB: PostgreSQL + pgvector")
    st.write("Backend: FastAPI")
    st.write("Frontend: Streamlit")

    st.markdown("---")

    if st.button("Clear Chat", width="stretch"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Healthcare RAG Assistant")
st.caption("Ask questions about patient records.")


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["type"] == "text":
            st.markdown(message["content"])

            # Show details only for assistant responses
            if message["role"] == "assistant" and "route" in message:
                with st.expander("Details"):
                    st.write(f"**Route:** {message['route'].upper()}")
                    st.write(f"**Execution Time:** {message['time']:.2f} s")

        elif message["type"] == "table":

            st.dataframe(
                pd.DataFrame(message["content"]),
                use_container_width=True
            )

            with st.expander("Details"):
                st.write(f"**Route:** {message['route'].upper()}")
                st.write(f"**Rows Returned:** {message['row_count']}")
                st.write(f"**Execution Time:** {message['time']:.2f} s")
                st.code(message["sql"], language="sql")


prompt = st.chat_input("Ask a healthcare question...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "type": "text",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            start = time.perf_counter()

            try:

                response = requests.post(
                    API_URL,
                    json={"message": prompt},
                    timeout=60
                )

                elapsed = time.perf_counter() - start

                response.raise_for_status()

                result = response.json()

            except requests.exceptions.Timeout:

                st.error("❌ Request timed out.")

                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "text",
                    "content": "Request timed out."
                })

                st.stop()

            except requests.exceptions.ConnectionError:

                st.error("❌ Cannot connect to FastAPI backend.")

                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "text",
                    "content": "Backend unavailable."
                })

                st.stop()

            except Exception as e:

                st.error(str(e))

                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "text",
                    "content": f"Error: {e}"
                })

                st.stop()

        if result["type"] == "table":

            rows = result.get("rows", [])
            sql = result.get("sql", "")
            route = result.get("route", "sql")

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True
            )

            with st.expander("Details"):
                st.write(f"**Route:** {route.upper()}")
                st.write(f"**Rows Returned:** {len(rows)}")
                st.write(f"**Execution Time:** {elapsed:.2f} s")
                st.code(sql, language="sql")

            st.session_state.messages.append({
                "role": "assistant",
                "type": "table",
                "route": route,
                "row_count": len(rows),
                "time": elapsed,
                "sql": sql,
                "content": rows
            })

        else:

            answer = result.get("answer", "")
            route = result.get("route", "rag")

            st.markdown(answer)

            with st.expander("Details"):
                st.write(f"**Route:** {route.upper()}")
                st.write(f"**Execution Time:** {elapsed:.2f} s")

            st.session_state.messages.append({
                "role": "assistant",
                "type": "text",
                "content": answer,
                "route": route,
                "time": elapsed
            })