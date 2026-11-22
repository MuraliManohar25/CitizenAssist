"""
CitizenAssist — src/translation.py
LLM-based translation between English and Telugu.
"""

import logging
from pathlib import Path
from typing import Optional

from src.rag import call_llm, load_prompt

logger = logging.getLogger(__name__)


SUPPORTED_LANGUAGES = {
    "English": "en",
    "Telugu": "te"
}

UI_STRINGS = {
    "English": {
        "app_tagline": "Understand. Check. Act.",
        "app_subtitle": "Government information, made understandable.",
        "select_language": "Select Language",
        "select_scheme": "Select a Government Scheme",
        "ask_tab": "🔍 Ask CitizenAssist",
        "eligibility_tab": "🎯 Check Eligibility",
        "guidance_tab": "🧭 What Should I Do Next?",
        "ask_placeholder": "Ask anything about this scheme...",
        "ask_button": "Get Answer",
        "check_eligibility": "Check My Eligibility",
        "simple_mode": "🧠 Explain Simply (plain language)",
        "disclaimer": (
            "**CitizenAssist** provides informational guidance based on available official government documents. "
            "It does not replace decisions or advice from the relevant government authority. "
            "Always verify important information with the official source before applying."
        ),
        "schemes_available": "Government Schemes",
        "languages_supported": "Languages",
        "evidence_backed": "Evidence-Backed",
        "explore_scheme": "Explore Scheme →",
        "eligibility_title": "Eligibility Assessment",
        "docs_title": "Required Documents & Next Steps",
        "type_question": "Type your question here...",
        "no_scheme_selected": "Please select a scheme first.",
        "vectorstore_not_ready": "⚠️ Document index not ready. Please run the ingestion pipeline first.",
        "admin_title": "Admin — Document Management",
        "upload_pdf": "Upload New PDF",
        "processing": "Processing...",
        "done": "Done!",
        "back_to_home": "← Back to Home",
        "condition_table_header": ["Eligibility Condition", "Your Information", "Result"],
        "why_eligible": "Why you appear eligible:",
        "why_not_eligible": "Why you appear not eligible:",
        "more_info_needed": "Information still needed:",
        "important_note": "⚠️ **Important**",
        "official_disclaimer": "Final eligibility is determined by the relevant government authority. CitizenAssist provides an informational assessment based on official documents. Always verify with the official source before applying.",
        "chat_history": "Conversation",
        "you": "You",
        "assistant": "CitizenAssist",
        "new_conversation": "New Conversation",
        "scheme_overview": "Scheme Overview",
        "target_users": "Who is this for?",
        "department": "Department",
        "state": "State/Coverage",
        "year": "Year"
    },
    "Telugu": {
        "app_tagline": "అర్థం చేసుకోండి. తనిఖీ చేయండి. చర్య తీసుకోండి.",
        "app_subtitle": "ప్రభుత్వ సమాచారం, సులభంగా అర్థమయ్యేలా.",
        "select_language": "భాష ఎంచుకోండి",
        "select_scheme": "ప్రభుత్వ పథకాన్ని ఎంచుకోండి",
        "ask_tab": "🔍 CitizenAssist అడగండి",
        "eligibility_tab": "🎯 అర్హత తనిఖీ",
        "guidance_tab": "🧭 తదుపరి ఏమి చేయాలి?",
        "ask_placeholder": "ఈ పథకం గురించి ఏమైనా అడగండి...",
        "ask_button": "సమాధానం పొందండి",
        "check_eligibility": "నా అర్హత తనిఖీ చేయండి",
        "simple_mode": "🧠 సులభంగా వివరించండి",
        "disclaimer": (
            "**CitizenAssist** అందుబాటులో ఉన్న అధికారిక ప్రభుత్వ పత్రాల ఆధారంగా సమాచార మార్గదర్శకత్వాన్ని అందిస్తుంది. "
            "ఇది సంబంధిత ప్రభుత్వ అధికారం యొక్క నిర్ణయాలు లేదా సలహాలను భర్తీ చేయదు. "
            "దరఖాస్తు చేసే ముందు ఎల్లప్పుడూ అధికారిక మూలంతో ముఖ్యమైన సమాచారాన్ని ధృవీకరించండి."
        ),
        "schemes_available": "ప్రభుత్వ పథకాలు",
        "languages_supported": "భాషలు",
        "evidence_backed": "సాక్ష్యాధారిత",
        "explore_scheme": "పథకాన్ని అన్వేషించండి →",
        "eligibility_title": "అర్హత అంచనా",
        "docs_title": "అవసరమైన పత్రాలు & తదుపరి దశలు",
        "type_question": "మీ ప్రశ్న ఇక్కడ టైప్ చేయండి...",
        "no_scheme_selected": "దయచేసి ముందు ఒక పథకాన్ని ఎంచుకోండి.",
        "vectorstore_not_ready": "⚠️ పత్రాల సూచిక సిద్ధంగా లేదు. దయచేసి ముందు ingestion pipeline నడపండి.",
        "admin_title": "అడ్మిన్ — పత్రాల నిర్వహణ",
        "upload_pdf": "కొత్త PDF అప్‌లోడ్ చేయండి",
        "processing": "ప్రాసెస్ చేస్తోంది...",
        "done": "పూర్తయింది!",
        "back_to_home": "← హోమ్‌కు తిరిగి వెళ్ళండి",
        "condition_table_header": ["అర్హత నిబంధన", "మీ సమాచారం", "ఫలితం"],
        "why_eligible": "మీరు అర్హులుగా కనిపించే కారణాలు:",
        "why_not_eligible": "మీరు అర్హులు కాదని కనిపించే కారణాలు:",
        "more_info_needed": "ఇంకా అవసరమైన సమాచారం:",
        "important_note": "⚠️ **ముఖ్యమైన గమనిక**",
        "official_disclaimer": "అంతిమ అర్హత సంబంధిత ప్రభుత్వ అధికారి నిర్ణయిస్తారు. CitizenAssist అధికారిక పత్రాల ఆధారంగా సమాచార అంచనాను అందిస్తుంది. దరఖాస్తు చేసే ముందు అధికారిక మూలాన్ని ధృవీకరించండి.",
        "chat_history": "సంభాషణ",
        "you": "మీరు",
        "assistant": "CitizenAssist",
        "new_conversation": "కొత్త సంభాషణ",
        "scheme_overview": "పథకం వివరణ",
        "target_users": "ఇది ఎవరి కోసం?",
        "department": "శాఖ",
        "state": "రాష్ట్రం/వ్యాప్తి",
        "year": "సంవత్సరం"
    }
}


def get_ui_string(key: str, language: str = "English") -> str:
    """Get a UI string in the specified language."""
    lang_strings = UI_STRINGS.get(language, UI_STRINGS["English"])
    return lang_strings.get(key, UI_STRINGS["English"].get(key, key))


def translate_text(
    text: str,
    target_language: str,
    source_language: str = "English",
    content_type: str = "general"
) -> str:
    """
    Translate text using the LLM.

    Args:
        text: Text to translate
        target_language: Target language ("English" or "Telugu")
        source_language: Source language
        content_type: Type of content (general/eligibility/documents/steps)

    Returns:
        Translated text
    """
    if source_language == target_language:
        return text

    if not text.strip():
        return text

    prompt_template = load_prompt("translation_prompt.txt")
    prompt = prompt_template.format(
        source_language=source_language,
        target_language=target_language,
        content_type=content_type,
        content=text
    )

    return call_llm(prompt, temperature=0.2)


def get_scheme_name(scheme: dict, language: str = "English") -> str:
    """Get scheme name in specified language."""
    if language == "Telugu":
        return scheme.get("name_te", scheme.get("name", ""))
    return scheme.get("name", "")


def get_field_label(field: dict, language: str = "English") -> str:
    """Get form field label in specified language."""
    if language == "Telugu":
        return field.get("label_te", field.get("label", ""))
    return field.get("label", "")
