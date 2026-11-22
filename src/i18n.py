"""
CitizenAssist — src/i18n.py
Internationalization (i18n) for English and Telugu.
"""

import streamlit as st

TEXT = {
    "en": {
        # App-wide
        "app_name": "CitizenAssist",
        "app_tagline": "Scheme guidance based on the documents in this service.",
        "language": "Language",
        "government_scheme": "Government scheme",
        
        # Navigation
        "nav_home": "Home",
        "nav_ask": "Ask a question",
        "nav_eligibility": "Check eligibility",
        "nav_admin": "Admin",
        
        # Home page
        "home_title": "Government Scheme Guidance",
        "home_subtitle": "Ask questions about government schemes in English or Telugu",
        "stat_schemes": "Schemes in this service",
        "stat_languages": "Languages",
        "stat_index": "Document index",
        "stat_ready": "Ready",
        "choose_scheme": "Choose this scheme",
        "for_scheme": "For:",
        "common_questions": "Common questions",
        "ask_anything": "Ask anything about this scheme",
        "disclaimer": "This service provides guidance based on official documents. Always verify with official sources before applying.",
        
        # Ask page
        "ask_title": "Ask a Question",
        "ask_placeholder": "Type your question here...",
        "simple_mode": "Explain in simple language",
        "new_conversation": "Start a new conversation",
        "documents_steps": "Documents and application steps",
        "scheme_overview": "Scheme overview",
        "load_documents": "Load documents and steps",
        "refresh_summary": "Refresh this summary",
        "not_enough_info": "The loaded documents do not contain enough information for this summary.",
        
        # Eligibility page
        "eligibility_title": "Check Eligibility",
        "eligibility_subtitle": "Answer a few questions to check if you may be eligible",
        "check_eligibility": "Check eligibility",
        "eligible": "You may be eligible for this scheme",
        "not_eligible": "You may not be eligible for this scheme",
        "uncertain": "Eligibility could not be determined",
        "reason": "Reason",
        "next_steps": "Next steps",
        "ask_question": "Ask a question",
        "check_another": "Check another scheme",
        
        # Admin page
        "admin_title": "Admin",
        "admin_login_title": "Admin Access",
        "admin_password": "Admin password",
        "admin_unlock": "Unlock admin",
        "admin_signout": "Sign out of admin",
        "index_status": "Document Index Status",
        "safe_update": "Safe update workflow",
        "config_status": "Configuration Status",
        "config_settings": "Configuration Settings:",
        
        # Errors
        "error_answer": "I could not prepare an answer right now. Please try again shortly or check the official source.",
        "error_documents": "The document summary could not be prepared. Please try again later.",
        "error_eligibility": "The eligibility assessment could not be completed right now. Please try again later.",
        "technical_details": "Technical details",
        
        # Labels
        "your_age": "Your Age",
        "state_of_residence": "State of Residence",
        "annual_income": "Annual Family Income (₹)",
        "category": "Category",
        "has_aadhaar": "Do you have an Aadhaar card?",
        "yes": "Yes",
        "no": "No",
        "not_sure": "Not sure",
    },
    "te": {
        # App-wide
        "app_name": "సిటిజన్ అసిస్ట్",
        "app_tagline": "ఈ సేవలోని పత్రాల ఆధారంగా పథకం మార్గదర్శకత్వం.",
        "language": "భాష",
        "government_scheme": "ప్రభుత్వ పథకం",
        
        # Navigation
        "nav_home": "హోమ్",
        "nav_ask": "ప్రశ్న అడగండి",
        "nav_eligibility": "అర్హత పరిశీలించండి",
        "nav_admin": "అడ్మిన్",
        
        # Home page
        "home_title": "ప్రభుత్వ పథకం మార్గదర్శకత్వం",
        "home_subtitle": "ప్రభుత్వ పథకాల గురించి ఇంగ్లీష్ లేదా తెలుగులో ప్రశ్నలు అడగండి",
        "stat_schemes": "ఈ సేవలోని పథకాలు",
        "stat_languages": "భాషలు",
        "stat_index": "పత్రాల సూచిక",
        "stat_ready": "సిద్ధం",
        "choose_scheme": "ఈ పథకాన్ని ఎంచుకోండి",
        "for_scheme": "కోసం:",
        "common_questions": "సాధారణ ప్రశ్నలు",
        "ask_anything": "ఈ పథకం గురించి ఏదైనా అడగండి",
        "disclaimer": "ఈ సేవ అధికారిక పత్రాల ఆధారంగా మార్గదర్శకత్వం అందిస్తుంది. దరఖాస్తు చేయడానికి ముందు ఎల్లప్పుడూ అధికారిక మూలాలతో ధృవీకరించండి.",
        
        # Ask page
        "ask_title": "ప్రశ్న అడగండి",
        "ask_placeholder": "మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి...",
        "simple_mode": "సులభంగా వివరించండి",
        "new_conversation": "కొత్త సంభాషణ ప్రారంభించండి",
        "documents_steps": "పత్రాలు మరియు దరఖాస్తు దశలు",
        "scheme_overview": "పథకం వివరాలు",
        "load_documents": "పత్రాలు మరియు దశలను లోడ్ చేయండి",
        "refresh_summary": "ఈ సారాంశాన్ని రిఫ్రెష్ చేయండి",
        "not_enough_info": "లోడ్ చేసిన పత్రాలలో ఈ సారాంశానికి సరిపడిన సమాచారం లేదు.",
        
        # Eligibility page
        "eligibility_title": "అర్హత పరిశీలించండి",
        "eligibility_subtitle": "మీరు అర్హులా ఉండవచ్చునా తనిఖీ చేయడానికి కొన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి",
        "check_eligibility": "అర్హత పరిశీలించండి",
        "eligible": "మీరు ఈ పథకానికి అర్హులవరంగా ఉండవచ్చు",
        "not_eligible": "మీరు ఈ పథకానికి అర్హులు కాకపోవచ్చు",
        "uncertain": "అర్హతను నిర్ధారించలేకపోయాము",
        "reason": "కారణం",
        "next_steps": "తదుపరి చర్యలు",
        "ask_question": "ప్రశ్న అడగండి",
        "check_another": "మరో పథకాన్ని పరిశీలించండి",
        
        # Admin page
        "admin_title": "అడ్మిన్",
        "admin_login_title": "అడ్మిన్ యాక్సెస్",
        "admin_password": "అడ్మిన్ పాస్వర్డ్",
        "admin_unlock": "అడ్మిన్ అన్లాక్ చేయండి",
        "admin_signout": "అడ్మిన్ నుండి సైన్ అవుట్",
        "index_status": "పత్రాల సూచిక స్థితి",
        "safe_update": "సురక్షిత అప్‌డేట్ వర్క్‌ఫ్లో",
        "config_status": "కాన్ఫిగరేషన్ స్థితి",
        "config_settings": "కాన్ఫిగరేషన్ సెట్టింగ్‌లు:",
        
        # Errors
        "error_answer": "క్షమించండి, ప్రస్తుతం సమాధానం రూపొందించలేకపోయాను. కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి లేదా అధికారిక మూలాన్ని చూడండి.",
        "error_documents": "పత్రాల సారాంశాన్ని ప్రస్తుతం రూపొందించలేకపోయాము. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి.",
        "error_eligibility": "అర్హత మదింపును ప్రస్తుతం పూర్తి చేయలేకపోయాము. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి.",
        "technical_details": "సాంకేతిక వివరాలు",
        
        # Labels
        "your_age": "మీ వయసు",
        "state_of_residence": "నివాస రాష్ట్రం",
        "annual_income": "వార్షిక కుటుంబ ఆదాయం (₹)",
        "category": "కేటగిరీ",
        "has_aadhaar": "మీకు ఆధార్ కార్డు ఉందా?",
        "yes": "అవును",
        "no": "కాదు",
        "not_sure": "ఖచ్చితంగా తెలియదు",
    }
}


def t(key: str) -> str:
    """
    Get translated text for the given key.
    
    Reads language from st.session_state["language"] (defaults to "en").
    Falls back to English if Telugu key is missing.
    """
    lang = st.session_state.get("language", "en")
    if lang == "te" and key in TEXT["te"]:
        return TEXT["te"][key]
    return TEXT["en"].get(key, key)
