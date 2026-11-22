"""CitizenAssist home page."""

from __future__ import annotations

import streamlit as st

from src.app_ui import (
    apply_global_styles,
    apply_page_config,
    initialise_session_state,
    load_schemes,
    render_sidebar,
    scheme_text,
    select_scheme,
    selected_scheme,
    vectorstore_dir,
)


apply_page_config("CitizenAssist")
initialise_session_state()
apply_global_styles()

schemes = load_schemes()
language = render_sidebar(schemes, active_page="home")
current_scheme = selected_scheme(schemes)
index_ready = (vectorstore_dir() / "faiss.index").exists()

st.markdown("<p class='ca-kicker'>PUBLIC-SERVICE SCHEME GUIDANCE</p>", unsafe_allow_html=True)
st.title("Understand a scheme before you apply")
st.markdown(
    "<p class='ca-lead'>Choose a government scheme to ask grounded questions, review the application guidance, or make an informational eligibility check.</p>",
    unsafe_allow_html=True,
)

if not index_ready:
    st.error(
        "The document index is not ready, so answers cannot yet be grounded in the scheme documents. "
        "An administrator must build the index before this service is used."
    )

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Schemes in this service", len(schemes))
metric_2.metric("Languages", "English and Telugu")
metric_3.metric("Document index", "Ready" if index_ready else "Not ready")

st.divider()
st.header("Choose a scheme")
st.caption("Select the programme that best matches the help you need. You can change it at any time.")

for row_start in range(0, len(schemes), 2):
    row = schemes[row_start : row_start + 2]
    columns = st.columns(2)
    for column, scheme in zip(columns, row):
        with column:
            with st.container(border=True):
                scheme_name = scheme_text(scheme, "name", language)
                st.subheader(f"{scheme.get('icon', '')} {scheme_name}")
                st.caption(scheme_text(scheme, "department", language))
                st.write(scheme_text(scheme, "short_description", language))
                st.caption(f"For: {scheme_text(scheme, 'target_users', language)}")
                is_selected = current_scheme and current_scheme.get("id") == scheme.get("id")
                button_label = "Selected" if is_selected else "Choose this scheme"
                if st.button(
                    button_label,
                    key=f"select_scheme_{scheme['id']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    select_scheme(str(scheme["id"]))
                    st.switch_page("pages/1_Ask.py")

if current_scheme:
    st.divider()
    current_name = scheme_text(current_scheme, "name", language)
    st.header(f"Selected: {current_name}")
    st.caption("Your conversation and eligibility assessment are kept only for this browser session.")
    action_1, action_2 = st.columns(2)
    with action_1:
        if st.button("Ask a question", type="primary", use_container_width=True):
            st.switch_page("pages/1_Ask.py")
    with action_2:
        if st.button("Check eligibility", use_container_width=True):
            st.switch_page("pages/2_Eligibility.py")

st.divider()
st.warning(
    "CitizenAssist provides informational guidance from the documents loaded into this service. "
    "It does not decide eligibility or replace the relevant government authority. Verify important details with the official source before applying."
)
