"""Protected operational status page for CitizenAssist."""

from __future__ import annotations

import hmac
import json
import os

import streamlit as st

from src.app_ui import (
    admin_is_enabled,
    apply_global_styles,
    apply_page_config,
    initialise_session_state,
    load_schemes,
    render_sidebar,
    vectorstore_dir,
)


def admin_login() -> bool:
    expected_password = os.getenv("ADMIN_PASSWORD", "")
    if not expected_password:
        return False
    if st.session_state.get("admin_authenticated"):
        return True

    with st.form("admin_login"):
        password = st.text_input("Admin password", type="password")
        submitted = st.form_submit_button("Unlock admin")
    if submitted:
        if hmac.compare_digest(password, expected_password):
            st.session_state.admin_authenticated = True
            st.rerun()
        st.error("That password is not correct.")
    return False


apply_page_config("Admin")
initialise_session_state()
apply_global_styles()

schemes = load_schemes()
render_sidebar(schemes, active_page="admin")

st.title("Admin")

if not admin_is_enabled():
    st.error("The admin page is disabled because ADMIN_PASSWORD is not configured.")
    st.info("Set a strong ADMIN_PASSWORD as a deployment secret to enable this page. The public service does not need admin access to run.")
    st.stop()

if not admin_login():
    st.caption("Administrative access is restricted. Do not share this password with service users.")
    st.stop()

vector_dir = vectorstore_dir()
index_file = vector_dir / "faiss.index"
chunks_file = vector_dir / "chunks.json"

st.caption("Operational status only. Update scheme documents through the reviewed source repository and rebuild the index in the deployment workflow.")

chunk_count = 0
indexed_schemes: dict[str, dict[str, object]] = {}
if chunks_file.exists():
    try:
        with chunks_file.open("r", encoding="utf-8") as chunk_file:
            chunks = json.load(chunk_file)
        chunk_count = len(chunks)
        for chunk in chunks:
            scheme_id = str(chunk.get("scheme_id", "unknown"))
            item = indexed_schemes.setdefault(
                scheme_id,
                {"name": chunk.get("scheme_name", scheme_id), "pages": set(), "chunks": 0},
            )
            item["chunks"] = int(item["chunks"]) + 1
            item["pages"].add(chunk.get("page_number"))
    except (OSError, json.JSONDecodeError):
        st.warning("The chunk metadata could not be read. Rebuild the index in the deployment workflow.")

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Vector index", "Ready" if index_file.exists() else "Not ready")
metric_2.metric("Indexed chunks", chunk_count)
metric_3.metric("Configured schemes", len(schemes))

st.divider()
st.header("Indexed documents")
if indexed_schemes:
    for scheme_id, details in sorted(indexed_schemes.items()):
        with st.container(border=True):
            st.subheader(str(details["name"]))
            st.caption(
                f"{details['chunks']} chunks across {len(details['pages'])} pages. Scheme ID: {scheme_id}"
            )
else:
    st.info("No indexed document metadata is available.")

st.divider()
st.header("Safe update workflow")
st.markdown(
    "1. Verify that each replacement PDF is an official source and record its origin.\n"
    "2. Update the scheme metadata and PDF in the source-controlled project.\n"
    "3. Run `python scripts/ingest_all.py` in the build workflow.\n"
    "4. Validate citations and a sample question before releasing the deployment."
)

if st.button("Sign out of admin", use_container_width=True):
    st.session_state.pop("admin_authenticated", None)
    st.rerun()
