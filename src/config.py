"""
CitizenAssist — src/config.py
Centralized configuration management for local and Cloud deployments.
"""

import os
from pathlib import Path
from typing import Any, Optional

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_setting(name: str, default: Optional[Any] = None) -> Any:
    """
    Get a configuration setting, checking in order:
    1. Streamlit secrets (Cloud)
    2. Environment variables (local .env or system)
    3. Default value
    
    Args:
        name: Configuration variable name
        default: Default value if not found
        
    Returns:
        The configuration value
    """
    # Check Streamlit secrets first (Cloud)
    try:
        value = st.secrets.get(name)
        if value is not None:
            return value
    except Exception:
        # st.secrets may not be available in all contexts
        pass
    
    # Fall back to environment variables
    value = os.getenv(name)
    if value is not None:
        return value
    
    # Return default
    return default


def get_config_status() -> dict[str, Any]:
    """
    Get the status of all configuration settings for debugging.
    Returns only whether keys are set, never the actual API key.
    """
    return {
        "GOOGLE_API_KEY": bool(get_setting("GOOGLE_API_KEY", "")),
        "LLM_MODEL": get_setting("LLM_MODEL", "gemini-3.5-flash-lite"),
        "EMBEDDING_MODEL": get_setting("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        "RAG_TOP_K": get_setting("RAG_TOP_K", "5"),
        "RAG_MIN_SIMILARITY": get_setting("RAG_MIN_SIMILARITY", "0.20"),
        "VECTORSTORE_PATH": get_setting("VECTORSTORE_PATH", "vectorstore"),
        "ADMIN_PASSWORD": bool(get_setting("ADMIN_PASSWORD", "")),
    }
