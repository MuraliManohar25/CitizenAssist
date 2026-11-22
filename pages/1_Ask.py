"""Grounded scheme question-and-answer experience."""

from __future__ import annotations

import hashlib
import time
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
from src.i18n import t
from src.voice import transcribe, clean_for_speech, synthesize


def question_suggestions(language: str) -> list[str]:
    if language == "Telugu":
        return [
            "ఈ పథకం గురించి సులభంగా వివరించండి",
            "అర్హత నిబంధనలు ఏమిటి?",
            "ఏ పత్రాలు అవసరం?",
            "దరఖాస్తు ఎలా చేయాలి?",
        ]
    return [
        "Explain this scheme simply",
        "Who is eligible to apply?",
        "What documents do I need?",
        "How do I apply?",
    ]


def render_sources(sources: list[dict[str, object]], language: str) -> None:
    if not sources:
        return
    source_heading = "మూలాలు" if language == "Telugu" else "Sources"
    with st.expander(source_heading):
        seen: set[tuple[object, object, object]] = set()
        for source in sources:
            fingerprint = (source.get("document"), source.get("page"), source.get("section"))
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            document = str(source.get("document", "Scheme document"))
            page = source.get("page", "?")
            section = str(source.get("section", "")).strip()
            citation = f"{document}, page {page}"
            if section and section != "General":
                citation = f"{citation}, {section}"
            st.markdown(f"- {citation}")


apply_page_config("Ask a question")
initialise_session_state()
apply_global_styles()

# Initialize voice-related session state
if "mic_counter" not in st.session_state:
    st.session_state.mic_counter = 0
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "last_voice_time" not in st.session_state:
    st.session_state.last_voice_time = 0
if "auto_voice" not in st.session_state:
    st.session_state.auto_voice = False
if "voice_audio_cache" not in st.session_state:
    st.session_state.voice_audio_cache = {}

schemes = load_schemes()
language = render_sidebar(schemes, active_page="ask")
scheme = selected_scheme(schemes)

st.markdown("<p class='ca-kicker'>DOCUMENT-GROUNDED ANSWERS</p>", unsafe_allow_html=True)
st.title("Ask about a government scheme")

if not scheme:
    st.info("Choose a scheme from the sidebar before asking a question.")
    st.stop()

if not (vectorstore_dir() / "faiss.index").exists():
    st.error("The document index is not ready. Answers are unavailable until an administrator builds it.")
    st.stop()

scheme_name = scheme_text(scheme, "name", language)
st.markdown(
    f"<p class='ca-lead'>You are asking about <strong>{escape_html(scheme_name)}</strong>. Answers should be checked against the cited source pages.</p>",
    unsafe_allow_html=True,
)

with st.expander("What this service can and cannot do"):
    st.markdown(
        "It can explain the material in the loaded document and point to the relevant pages. "
        "It cannot make a final government decision, confirm a live deadline, or replace the official application portal."
    )

suggestion_label = "త్వరిత ప్రశ్న" if language == "Telugu" else "Common question"
ask_suggestion = "ఈ ప్రశ్న అడగండి" if language == "Telugu" else "Use this question"
choice_column, action_column = st.columns([4, 1])
with choice_column:
    suggestion = st.selectbox(suggestion_label, [""] + question_suggestions(language), format_func=lambda item: item or "Select a question")
with action_column:
    st.write("")
    if st.button(ask_suggestion, use_container_width=True, disabled=not suggestion):
        st.session_state.pending_question = suggestion
        st.rerun()

for message in st.session_state.chat_history:
    with st.chat_message(message.get("role", "assistant")):
        st.markdown(str(message.get("content", "")))
        render_sources(list(message.get("sources", [])), language)
        
        # Add TTS listen button for assistant messages
        if message.get("role") == "assistant":
            msg_idx = len(st.session_state.chat_history) - 1 - list(reversed(st.session_state.chat_history)).index(message)
            cache_key = f"audio_{msg_idx}"
            
            if st.button(t("listen"), key=f"listen_{msg_idx}"):
                cleaned_text = clean_for_speech(message.get("content", ""), language)
                if cleaned_text:
                    audio_bytes = synthesize(cleaned_text, language)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        st.session_state.voice_audio_cache[cache_key] = audio_bytes
                    else:
                        st.warning(t("voice_unavailable"))
            
            # Auto-play if enabled and this is a new answer
            if st.session_state.auto_voice and cache_key not in st.session_state.voice_audio_cache:
                cleaned_text = clean_for_speech(message.get("content", ""), language)
                if cleaned_text:
                    audio_bytes = synthesize(cleaned_text, language)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        st.session_state.voice_audio_cache[cache_key] = audio_bytes

# Voice input section
st.caption(t("voice_privacy"))
audio_input = st.audio_input(
    t("voice_prompt"),
    key=f"mic_{st.session_state.mic_counter}"
)

# Handle voice transcription
if audio_input is not None:
    current_time = time.time()
    if current_time - st.session_state.last_voice_time < 3:
        st.warning("Please wait a moment before recording again.")
    else:
        st.session_state.last_voice_time = current_time
        
        # Calculate hash to detect duplicate submissions
        audio_hash = hashlib.sha256(audio_input).hexdigest()
        
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            
            try:
                lang_code = "te" if language == "Telugu" else "en"
                transcript = transcribe(audio_input, lang_code)
                
                if not transcript or len(transcript) < 2:
                    st.warning(t("voice_not_heard"))
                else:
                    st.session_state.pending_question = transcript
                    st.session_state.mic_counter += 1
                    st.rerun()
            except Exception as e:
                if "Rate limit" in str(e):
                    st.error(t("voice_rate_limited"))
                else:
                    st.error(str(e))

typed_question = st.chat_input(
    "మీ ప్రశ్నను టైప్ చేయండి" if language == "Telugu" else "Ask anything about this scheme"
)
question = typed_question or st.session_state.pop("pending_question", None)

if question:
    question = question.strip()
    if not question:
        st.stop()

    st.session_state.chat_history.append({"role": "user", "content": question, "sources": []})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("సమాచారాన్ని పరిశీలిస్తోంది..." if language == "Telugu" else "Reviewing the scheme documents..."):
            try:
                from src.rag import get_rag_pipeline

                result = get_rag_pipeline(str(vectorstore_dir())).answer(
                    question=question,
                    scheme_id=str(scheme["id"]),
                    scheme_name=scheme_name,
                    language=language,
                    conversation_history=st.session_state.chat_history[:-1],
                    simple_mode=bool(st.session_state.simple_mode),
                )
                answer = str(result["answer"])
                sources = list(result.get("sources", []))
                st.markdown(answer)
                render_sources(sources, language)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except Exception as e:
                safe_error = (
                    "క్షమించండి, ప్రస్తుతం సమాధానం రూపొందించలేకపోయాను. కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి లేదా అధికారిక మూలాన్ని చూడండి."
                    if language == "Telugu"
                    else "I could not prepare an answer right now. Please try again shortly or check the official source."
                )
                st.error(safe_error)
                with st.expander("Technical details"):
                    st.code(f"{type(e).__name__}: {str(e)}")
                # Store error separately, not in chat history for LLM
                st.session_state.chat_history.append(
                    {"role": "error", "content": safe_error, "sources": []}
                )

st.divider()
documents_tab, overview_tab = st.tabs(
    ["Documents and application steps", "Scheme overview"]
    if language == "English"
    else ["పత్రాలు మరియు దరఖాస్తు దశలు", "పథకం వివరాలు"]
)

with documents_tab:
    st.write("Review a document-grounded summary of the documents and application process.")
    content_is_current = st.session_state.get("docs_steps_scheme_id") == scheme.get("id")
    if not content_is_current:
        if st.button("Load documents and steps", type="primary"):
            with st.spinner("Reviewing the source document..."):
                try:
                    from src.rag import get_rag_pipeline

                    st.session_state.docs_steps_content = get_rag_pipeline(str(vectorstore_dir())).get_documents_and_steps(
                        str(scheme["id"]), scheme_name, language
                    )
                    st.session_state.docs_steps_scheme_id = scheme["id"]
                    st.rerun()
                except Exception as e:
                    st.error("The document summary could not be prepared. Please try again later.")
                    with st.expander("Technical details"):
                        st.code(f"{type(e).__name__}: {str(e)}")
    else:
        document_result = st.session_state.get("docs_steps_content", {})
        if document_result.get("content"):
            st.markdown(str(document_result["content"]))
            render_sources(list(document_result.get("sources", [])), language)
        else:
            st.info("The loaded documents do not contain enough information for this summary.")
        if st.button("Refresh this summary"):
            st.session_state.pop("docs_steps_content", None)
            st.session_state.pop("docs_steps_scheme_id", None)
            st.rerun()

with overview_tab:
    st.subheader(f"{scheme.get('icon', '')} {scheme_name}")
    detail_1, detail_2 = st.columns(2)
    with detail_1:
        st.markdown(f"**Department:** {scheme_text(scheme, 'department', language)}")
        st.markdown(f"**Coverage:** {scheme_text(scheme, 'state', language)}")
    with detail_2:
        st.markdown(f"**Target group:** {scheme_text(scheme, 'target_users', language)}")
        st.markdown(f"**Document year:** {scheme_text(scheme, 'year', language)}")
    st.write(scheme_text(scheme, "short_description", language))
    if st.button("Check eligibility", type="primary"):
        st.switch_page("pages/2_Eligibility.py")
