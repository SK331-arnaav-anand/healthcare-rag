# Healthcare RAG Assistant

A hybrid SQL + RAG chatbot for querying structured healthcare records using natural language.

The application intelligently routes user queries to either:
- **SQL** for filtering, aggregation and multi-record retrieval.
- **RAG** for semantic question answering over individual patient records.

## Tech Stack

- Python
- FastAPI
- Streamlit
- PostgreSQL + pgvector
- Google Gemini 2.5 Flash
- Sentence Transformers (all-MiniLM-L6-v2)
- Amazon S3
- ngrok

## Running Locally

Clone the repository:

```bash
git clone <repository-url>
cd healthcare-rag
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key

AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=...

DB_HOST=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_PORT=5432
```

Enable the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Ingest the dataset:

```bash
python vector_ingestion.py
```

Start the FastAPI backend:

```bash
uvicorn app:app --reload
```

Expose the API using ngrok:

```bash
ngrok http 8000
```

Copy the generated public URL (e.g. `https://xxxxx.ngrok-free.app`) and update the `API_URL` in `streamlit_app.py`:

```python
API_URL = "https://xxxxx.ngrok-free.app/chat"
```

Finally, start the frontend:

```bash
streamlit run streamlit_app.py
```

The application will be available at:

- Streamlit: `http://localhost:8501`
- FastAPI Docs: `http://localhost:8000/docs`
- Public API: `https://<your-ngrok-url>/chat`

