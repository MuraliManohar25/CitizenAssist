"""Informational eligibility assessment for a selected scheme."""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.app_ui import (
    apply_global_styles,
    apply_page_config,
    escape_html,
    initialise_session_state,
    load_schemes,
    render_sidebar,
    scheme_text,
    selected_scheme,
    vectorstore_dir,
)


STATUS_MESSAGES = {
    "LIKELY_ELIGIBLE": ("success", "Likely eligible"),
    "LIKELY_NOT_ELIGIBLE": ("error", "May not be eligible"),
    "MORE_INFO_NEEDED": ("warning", "More information is needed"),
}


def render_field(field: dict[str, Any], language: str) -> tuple[str, Any]:
    """Render one form field, returning its label and an optional response."""
    label = str(field.get("label_te", field["label"]) if language == "Telugu" else field["label"])
    key = f"eligibility_{field['key']}"
    field_type = field.get("type", "text")

    if field_type == "number":
        value = st.number_input(
            label,
            min_value=field.get("min", 0),
            max_value=field.get("max", 10_000_000),
            value=None,
            step=1,
            placeholder="Enter a number",
            key=key,
        )
        return label, value

    options = list(field.get("options", []))
    if field_type == "select" and options:
        placeholder = "ఎంచుకోండి" if language == "Telugu" else "Select an option"
        value = st.selectbox(label, options, index=None, placeholder=placeholder, key=key)
        return label, value

    value = st.text_input(label, key=key)
    return label, value.strip() or None


def render_sources(sources: list[dict[str, object]]) -> None:
    if not sources:
        return
    with st.expander("Official document references"):
        seen: set[tuple[object, object]] = set()
        for source in sources:
            fingerprint = (source.get("document"), source.get("page"))
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            st.markdown(f"- {source.get('document', 'Scheme document')}, page {source.get('page', '?')}")


def render_result(result: dict[str, Any], language: str) -> None:
    status = str(result.get("overall_status", "MORE_INFO_NEEDED"))
    method_name, default_heading = STATUS_MESSAGES.get(status, STATUS_MESSAGES["MORE_INFO_NEEDED"])
    heading = default_heading
    explanation = str(result.get("overall_explanation_te") or result.get("overall_explanation", ""))

    getattr(st, method_name)(heading)
    if explanation:
        st.write(explanation)

    conditions = result.get("conditions", [])
    if isinstance(conditions, list) and conditions:
        st.subheader("Condition-by-condition assessment" if language == "English" else "నిబంధనల వారీ అంచనా")
        for condition in conditions:
            if not isinstance(condition, dict):
                continue
            condition_status = str(condition.get("status", "UNKNOWN")).upper()
            condition_name = str(
                condition.get("condition_name_te") or condition.get("condition_name") or "Eligibility condition"
            )
            explanation = str(condition.get("explanation_te") or condition.get("explanation") or "")
            user_value = condition.get("user_value")
            document_requirement = str(condition.get("document_requirement", ""))
            label = {
                "PASS": "Satisfied",
                "FAIL": "Not satisfied",
                "UNKNOWN": "More information needed",
                "NOT_FOUND": "Not found in the document",
            }.get(condition_status, "More information needed")

            with st.container(border=True):
                st.markdown(f"**{condition_name}**")
                st.caption(label)
                if document_requirement:
                    st.write(f"Document requirement: {document_requirement}")
                if user_value not in (None, ""):
                    st.write(f"Your response: {user_value}")
                if explanation:
                    st.write(explanation)

    why = result.get("why_explanation", {})
    if isinstance(why, dict):
        sections = [
            ("Why this may help", why.get("passed_conditions", [])),
            ("Why this may prevent eligibility", why.get("failed_conditions", [])),
            ("Information still needed", why.get("unknown_conditions", [])),
        ]
        for title, items in sections:
            if isinstance(items, list) and items:
                st.subheader(title)
                for item in items:
                    st.markdown(f"- {item}")

    render_sources(list(result.get("sources", [])))
    disclaimer = str(result.get("disclaimer_te") or result.get("disclaimer") or "")
    if disclaimer:
        st.warning(disclaimer)


apply_page_config("Check eligibility")
initialise_session_state()
apply_global_styles()

schemes = load_schemes()
language = render_sidebar(schemes, active_page="eligibility")
scheme = selected_scheme(schemes)

st.markdown("<p class='ca-kicker'>INFORMATIONAL ELIGIBILITY CHECK</p>", unsafe_allow_html=True)
st.title("Check whether you may be eligible")

if not scheme:
    st.info("Choose a scheme from the sidebar before starting an eligibility check.")
    st.stop()
if not (vectorstore_dir() / "faiss.index").exists():
    st.error("The document index is not ready. Eligibility checks are unavailable until it has been built.")
    st.stop()

scheme_name = scheme_text(scheme, "name", language)
st.markdown(
    f"<p class='ca-lead'>Answer only the questions you are comfortable answering. This is an informational check for <strong>{escape_html(scheme_name)}</strong>, not a government decision.</p>",
    unsafe_allow_html=True,
)

fields = list(scheme.get("eligibility_fields", []))
user_info: dict[str, Any] = {}
with st.form("eligibility_form", clear_on_submit=False):
    st.subheader("Your information" if language == "English" else "మీ సమాచారం")
    st.caption("Your answers are used for this browser session and are not written to the document index.")
    columns = st.columns(2)
    for index, field in enumerate(fields):
        with columns[index % 2]:
            label, value = render_field(field, language)
            if value not in (None, ""):
                user_info[label] = value
    submitted = st.form_submit_button(
        "Check eligibility" if language == "English" else "అర్హతను తనిఖీ చేయండి",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not user_info:
        st.warning("Provide at least one response to start the assessment.")
    else:
        with st.spinner("Reviewing the scheme conditions in the document..."):
            try:
                from src.eligibility import get_eligibility_checker

                assessment = get_eligibility_checker(str(vectorstore_dir())).check(
                    scheme_id=str(scheme["id"]),
                    scheme_name=scheme_name,
                    user_info=user_info,
                    language=language,
                )
                st.session_state.eligibility_result = assessment
                st.session_state.eligibility_scheme = scheme["id"]
            except Exception:
                st.error("The eligibility assessment could not be completed right now. Please try again later.")

if st.session_state.get("eligibility_scheme") == scheme.get("id"):
    assessment = st.session_state.get("eligibility_result")
    if isinstance(assessment, dict):
        st.divider()
        render_result(assessment, language)
        action_1, action_2 = st.columns(2)
        with action_1:
            if st.button("Ask a question", type="primary", use_container_width=True):
                st.switch_page("pages/1_Ask.py")
        with action_2:
            if st.button("Start a new assessment", use_container_width=True):
                st.session_state.pop("eligibility_result", None)
                st.session_state.pop("eligibility_scheme", None)
                st.rerun()
