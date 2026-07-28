import time
import requests
import pandas as pd
import streamlit as st

# API_URL = "http://127.0.0.1:8000/chat"
API_URL = "https://outing-grape-runny.ngrok-free.dev/chat"

st.set_page_config(
    page_title="Healthcare RAG Assistant",
    layout="wide"
)

st.title("Healthcare RAG Assistant")
st.caption("Ask questions about patient records.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["type"] == "text":

            st.markdown(message["content"])

            if message["role"] == "assistant":

                with st.expander("Details"):

                    st.write(f"**Route:** {message['route'].upper()}")
                    st.write(f"**Execution Time:** {message['time']:.2f} s")
                    st.write(f"**Total Tokens:** {message.get('tokens', '-')}")

        elif message["type"] == "table":

            st.dataframe(
                pd.DataFrame(message["content"]),
                width='stretch'
            )

            with st.expander("Details"):

                st.write(f"**Route:** {message['route'].upper()}")
                st.write(f"**Rows Returned:** {message['row_count']}")
                st.write(f"**Execution Time:** {message['time']:.2f} s")
                st.write(f"**Total Tokens:** {message.get('tokens', '-')}")
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

                # Keep only last 6 messages.
                history = []

                for msg in st.session_state.messages[-6:]:
                    if msg["type"] == "table":
                        history.append({
                            "role": msg["role"],
                            "content": f"Returned {msg['row_count']} patient records."
                        })

                    else:

                        history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

                response = requests.post(
                    API_URL,
                    json={
                        "message": prompt,
                        "history": history
                    },
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
            tokens = result.get("token_usage", "-")

            st.dataframe(
                pd.DataFrame(rows),
                width='stretch'
            )

            with st.expander("Details"):

                st.write(f"**Route:** {route.upper()}")
                st.write(f"**Rows Returned:** {len(rows)}")
                st.write(f"**Execution Time:** {elapsed:.2f} s")
                st.write(f"**Total Tokens:** {tokens}")
                st.code(sql, language="sql")

            st.session_state.messages.append({
                "role": "assistant",
                "type": "table",
                "route": route,
                "row_count": len(rows),
                "time": elapsed,
                "tokens": tokens,
                "sql": sql,
                "content": rows
            })

        else:

            answer = result.get("answer", "")
            route = result.get("route", "rag")
            tokens = result.get("token_usage", "-")

            st.markdown(answer)

            with st.expander("Details"):

                st.write(f"**Route:** {route.upper()}")
                st.write(f"**Execution Time:** {elapsed:.2f} s")
                st.write(f"**Total Tokens:** {tokens}")

            st.session_state.messages.append({
                "role": "assistant",
                "type": "text",
                "content": answer,
                "route": route,
                "time": elapsed,
                "tokens": tokens
            })

st.divider()

if st.button(
    "Clear chat",
    disabled=len(st.session_state.messages) == 0
):
    st.session_state.messages = []
    st.rerun()