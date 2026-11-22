# CitizenAssist

CitizenAssist is a Streamlit RAG application that helps people explore government-scheme documents, review cited answers, and make an informational eligibility assessment in English or Telugu.

## Important content notice

The PDFs bundled in `data/schemes/` were generated as demonstration material for this project. They are not a substitute for authoritative government publications. Before a public release, replace every demo PDF with a verified official source, record its origin and publication date, then rebuild the vector index. The interface intentionally labels results as informational guidance and never as a government decision.

## What it does

- Retrieves answers from the loaded scheme documents and displays their document-page references.
- Lets people ask questions in English or Telugu, with an optional plain-language mode.
- Provides an informational eligibility assessment based only on retrieved conditions.
- Keeps chat and form answers in the current browser session rather than storing them in the vector index.
- Disables the Admin page unless `ADMIN_PASSWORD` is configured as a deployment secret.

## Run locally

Use Python 3.11 for a deployment-compatible environment.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/ingest_all.py
python -m streamlit run app.py
```

Set `GOOGLE_API_KEY` in `.env` before asking questions. The app opens at `http://localhost:8501`.

## Environment settings

| Variable | Required | Purpose |
| --- | --- | --- |
| `GOOGLE_API_KEY` | Yes for AI answers | Google GenAI credential, stored only in `.env` locally or the host secret manager. |
| `LLM_MODEL` | No | Gemini model, default `gemini-3.5-flash-lite`. |
| `EMBEDDING_MODEL` | No | Sentence-transformer model, default `all-MiniLM-L6-v2`. |
| `RAG_TOP_K` | No | Number of relevant chunks considered, default `5`. |
| `RAG_MIN_SIMILARITY` | No | Retrieval threshold, default `0.20`. |
| `VECTORSTORE_PATH` | No | Index folder, default `./vectorstore`. |
| `ADMIN_PASSWORD` | No | Enables the protected Admin status page. Leave unset to keep it disabled. |

## Update the knowledge base

1. Confirm each PDF is official, current, and permitted to be used.
2. Replace the matching file in `data/schemes/` and update its metadata in `schemes_config.json`.
3. Run `python scripts/ingest_all.py` from the repository root.
4. On a fresh deployment, the sentence-transformer model downloads once when the first document search runs. Later searches use the cached model snapshot.
5. Check at least one answer, citation, and eligibility assessment for every changed scheme.
6. Commit the revised PDFs, `schemes_config.json`, and `vectorstore/` together so the deployed app uses matching data and index files.

## Deploy to Streamlit Community Cloud

1. Create a private GitHub repository and push this project. Do not include `.env`.
2. In Streamlit Community Cloud, create an app from that repository with `app.py` as the entrypoint.
3. Add `GOOGLE_API_KEY` in the host's secrets or environment-variable settings.
4. Only if you need operations access, add a strong `ADMIN_PASSWORD` there as well.
5. Confirm the index files in `vectorstore/` are present in the repository. The hosted app reads the prebuilt index at startup.
6. Open the deployed service and test a cited question, a Telugu answer, and an eligibility assessment before sharing the link.

Choose Python 3.11 from Community Cloud's Advanced settings and use the same version locally. The included `.streamlit/config.toml` defines the production theme.

## Project layout

```text
app.py                    Home and scheme selection
pages/1_Ask.py            Grounded chat and document summary
pages/2_Eligibility.py    Informational eligibility assessment
pages/3_Admin.py          Password-protected operational status
src/                      RAG, retrieval, ingestion, UI helpers
data/schemes/             Source PDFs
vectorstore/              Prebuilt FAISS index and metadata
```
