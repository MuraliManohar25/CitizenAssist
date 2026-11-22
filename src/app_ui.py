"""Shared presentation and state helpers for the CitizenAssist Streamlit app."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any, Iterable

import streamlit as st
from dotenv import load_dotenv

from src.config import get_setting

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = ("English", "Telugu")

load_dotenv(PROJECT_ROOT / ".env")


def project_path(*parts: str) -> Path:
    """Return a path rooted at the project, regardless of the launch directory."""
    return PROJECT_ROOT.joinpath(*parts)


def vectorstore_dir() -> Path:
    configured_path = Path(get_setting("VECTORSTORE_PATH", "vectorstore"))
    if not configured_path.is_absolute():
        configured_path = PROJECT_ROOT / configured_path
    return configured_path.resolve()


@st.cache_data(show_spinner=False)
def load_schemes() -> list[dict[str, Any]]:
    config_path = project_path("schemes_config.json")
    with config_path.open("r", encoding="utf-8") as config_file:
        data = json.load(config_file)

    schemes = data.get("schemes")
    if not isinstance(schemes, list):
        raise ValueError("schemes_config.json must contain a 'schemes' list.")
    return schemes


def initialise_session_state() -> None:
    defaults: dict[str, Any] = {
        "language": "English",
        "selected_scheme_id": None,
        "chat_history": [],
        "simple_mode": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def selected_scheme(schemes: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    selected_id = st.session_state.get("selected_scheme_id")
    return next((scheme for scheme in schemes if scheme.get("id") == selected_id), None)


def select_scheme(scheme_id: str | None) -> None:
    """Select a scheme and clear state that belongs to the previous scheme."""
    if scheme_id == st.session_state.get("selected_scheme_id"):
        return

    st.session_state.selected_scheme_id = scheme_id
    for key in (
        "chat_history",
        "docs_steps_content",
        "docs_steps_scheme_id",
        "eligibility_result",
        "eligibility_scheme",
        "pending_question",
    ):
        st.session_state.pop(key, None)
    st.session_state.chat_history = []


def scheme_text(scheme: dict[str, Any], field: str, language: str) -> str:
    if language == "Telugu":
        return str(scheme.get(f"{field}_te", scheme.get(field, "")))
    return str(scheme.get(field, ""))


def escape_html(value: Any) -> str:
    return html.escape(str(value), quote=True)


def admin_is_enabled() -> bool:
    return bool(get_setting("ADMIN_PASSWORD", "").strip())


def apply_page_config(title: str, icon: str = "🇮🇳") -> None:
    st.set_page_config(
        page_title=f"{title} | CitizenAssist",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_global_styles() -> None:
    """Apply one accessible visual system to every app page."""
    st.markdown(
        """
        <style>
          :root {
            --ca-navy: #12305a;
            --ca-blue: #1769aa;
            --ca-blue-soft: #eaf4fb;
            --ca-ink: #162235;
            --ca-muted: #526277;
            --ca-canvas: #f5f8fb;
            --ca-surface: #ffffff;
            --ca-line: #cfdae5;
            --ca-success: #176a43;
            --ca-warning: #895400;
            --ca-danger: #a33030;
            --ca-radius: 12px;
          }

          html, body, [data-testid="stAppViewContainer"] {
            background: var(--ca-canvas) !important;
            color: var(--ca-ink) !important;
          }
          
          body, p, h1, h2, h3, h4, h5, h6, label, li, td, th, input, textarea, button, [data-testid="stMarkdownContainer"] {
            font-family: "Noto Sans Telugu", "Inter", system-ui, sans-serif;
          }
          
          /* Restore Material Symbols icon font */
          [data-testid="stIconMaterial"],
          [data-testid="stExpanderToggleIcon"],
          .material-symbols-rounded,
          span[class*="material"] {
            font-family: "Material Symbols Rounded" !important;
          }

          #MainMenu, footer { visibility: hidden; }
          [data-testid="stHeader"] { background: transparent; }
          .main .block-container {
            max-width: 1180px;
            padding: 2rem 2rem 3.5rem;
          }

          [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
            background: #ffffff !important;
            color: var(--ca-ink) !important;
            border: 1px solid #b6c8d9 !important;
          }
          [data-testid="stSidebar"] .stSelectbox svg { fill: var(--ca-ink) !important; }
          [data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            color: #F2F5FA !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
          }
          
          /* Final sidebar color rule - ensures all text is readable */
          [data-testid="stSidebar"], [data-testid="stSidebar"] * {
            color: #F2F5FA !important;
          }
          
          /* Fix sidebar button text color (e.g., Start new conversation) */
          [data-testid="stSidebar"] button,
          [data-testid="stSidebar"] button * {
            color: #0F2A5C !important;
          }

          h1, h2, h3 { color: var(--ca-ink) !important; letter-spacing: -0.02em; }
          h1 { font-size: clamp(2rem, 4vw, 3rem) !important; }
          p, li { color: var(--ca-ink); line-height: 1.65; }

          .ca-kicker {
            color: var(--ca-blue);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
          }
          .ca-lead { color: var(--ca-muted); font-size: 1.1rem; max-width: 62ch; }
          .ca-quiet { color: var(--ca-muted); font-size: 0.9rem; }

          .stButton > button {
            min-height: 2.7rem;
            border-radius: 9px !important;
            border: 1px solid var(--ca-blue) !important;
            font-weight: 700 !important;
            transition: transform 120ms ease, background 120ms ease, box-shadow 120ms ease;
            white-space: nowrap;
          }
          .stButton > button[kind="primary"] {
            background: var(--ca-blue) !important;
            color: #ffffff !important;
          }
          .stButton > button[kind="secondary"] {
            background: var(--ca-surface) !important;
            color: var(--ca-navy) !important;
          }
          .stButton > button:hover { box-shadow: 0 4px 12px rgba(18, 48, 90, 0.16); }
          .stButton > button:active { transform: translateY(1px); }
          .stButton > button:focus-visible,
          input:focus-visible,
          textarea:focus-visible { outline: 3px solid #85bce3 !important; outline-offset: 2px; }

          [data-testid="stMetric"] {
            background: var(--ca-surface);
            border: 1px solid var(--ca-line);
            border-radius: var(--ca-radius);
            padding: 1rem;
          }
          [data-testid="stChatMessage"] {
            background: var(--ca-surface);
            border: 1px solid var(--ca-line);
            border-radius: var(--ca-radius);
            padding: 0.85rem 1rem;
          }
          [data-testid="stExpander"] {
            background: var(--ca-surface);
            border: 1px solid var(--ca-line);
            border-radius: var(--ca-radius);
          }
          [data-testid="stForm"] {
            background: var(--ca-surface);
            border: 1px solid var(--ca-line);
            border-radius: var(--ca-radius);
            padding: 1rem;
          }

          @media (max-width: 768px) {
            .main .block-container { padding: 1.15rem 1rem 2.5rem; }
            h1 { font-size: 2rem !important; }
          }
          @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(schemes: list[dict[str, Any]], active_page: str) -> str:
    """Render common navigation and return the active language."""
    language = st.session_state.get("language", "English")
    current_id = st.session_state.get("selected_scheme_id")

    with st.sidebar:
        st.title("CitizenAssist")
        st.caption("Scheme guidance based on the documents in this service.")
        st.divider()

        language = st.selectbox(
            "Language / భాష",
            options=list(LANGUAGES),
            index=list(LANGUAGES).index(language) if language in LANGUAGES else 0,
        )
        st.session_state.language = language

        option_ids = [None] + [str(scheme["id"]) for scheme in schemes]
        option_labels = ["Choose a scheme"] + [
            f"{scheme.get('icon', '')} {scheme_text(scheme, 'name', language)}" for scheme in schemes
        ]
        selected_index = option_ids.index(current_id) if current_id in option_ids else 0
        chosen_index = st.selectbox(
            "Government scheme",
            options=list(range(len(option_labels))),
            index=selected_index,
            format_func=lambda index: option_labels[index],
        )
        chosen_id = option_ids[chosen_index]
        if chosen_id != current_id:
            select_scheme(chosen_id)
            st.rerun()

        st.divider()
        st.page_link("app.py", label="Home")
        st.page_link("pages/1_Ask.py", label="Ask a question")
        st.page_link("pages/2_Eligibility.py", label="Check eligibility")
        if admin_is_enabled():
            st.page_link("pages/3_Admin.py", label="Admin")

        if active_page == "ask":
            st.divider()
            simple_label = "సులభంగా వివరించండి" if language == "Telugu" else "Explain in simple language"
            st.session_state.simple_mode = st.toggle(simple_label, value=st.session_state.simple_mode)
            if st.button("Start a new conversation", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.pop("pending_question", None)
                st.rerun()

    return language
