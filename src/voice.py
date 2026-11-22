"""
CitizenAssist — src/voice.py
Voice input/output (Speech-to-Text and Text-to-Speech) using Google Gemini for STT
and edge-tts/gTTS for TTS.
"""

import logging
import re
import hashlib
import asyncio
import threading
from io import BytesIO
from typing import Optional

import streamlit as st

logger = logging.getLogger(__name__)


def transcribe(audio_bytes: bytes, lang: str) -> str:
    """
    Transcribe audio to text using Google Gemini.
    
    Args:
        audio_bytes: Raw audio bytes (WAV format)
        lang: Language code ("en" or "te")
    
    Returns:
        Transcribed text, or empty string if audio is silent
    
    Raises:
        Exception: On quota/rate-limit errors
    """
    if not audio_bytes or len(audio_bytes) < 1000:
        logger.info("Audio too short or empty")
        return ""
    
    # Cap audio at ~60 seconds (assuming 16kHz mono = ~1.9MB)
    if len(audio_bytes) > 2_000_000:
        logger.warning("Audio too long, truncating to ~60 seconds")
        audio_bytes = audio_bytes[:2_000_000]
    
    try:
        from google.genai import types
        from src.rag import get_llm, _llm_type, _llm_client
        
        get_llm()
        
        if _llm_type == "genai_new":
            from google import genai
            client, model_name = _llm_client
            
            lang_hint = "Telugu" if lang == "te" else "English"
            prompt = f"Transcribe this audio exactly as spoken, in its original language and script (Telugu in Telugu script, English in English). The audio is likely in {lang_hint}. Return only the transcript, no commentary."
            
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                    types.Part.from_text(text=prompt)
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                )
            )
            
            text = getattr(response, "text", None)
            if not text:
                logger.warning("Empty transcription response")
                return ""
            
            # Clean up any extra text the model might add
            transcript = text.strip()
            if len(transcript) < 2:
                logger.info("Transcription too short, likely silence")
                return ""
            
            logger.info(f"Transcription successful: {len(transcript)} chars")
            return transcript
            
        else:
            # genai_old - similar approach
            import google.generativeai as genai_old
            
            lang_hint = "Telugu" if lang == "te" else "English"
            prompt = f"Transcribe this audio exactly as spoken, in its original language and script (Telugu in Telugu script, English in English). The audio is likely in {lang_hint}. Return only the transcript, no commentary."
            
            response = _llm_client.generate_content([
                {
                    "mime_type": "audio/wav",
                    "data": audio_bytes
                },
                prompt
            ])
            
            text = getattr(response, "text", None)
            if not text:
                logger.warning("Empty transcription response")
                return ""
            
            transcript = text.strip()
            if len(transcript) < 2:
                logger.info("Transcription too short, likely silence")
                return ""
            
            logger.info(f"Transcription successful: {len(transcript)} chars")
            return transcript
            
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Check for rate limit errors
        if "429" in error_msg or "ResourceExhausted" in error_type or "quota" in error_msg.lower():
            logger.exception(f"STT rate limit error: {e}")
            raise Exception("Rate limit exceeded. Please try again in a minute.") from e
        
        logger.exception(f"STT transcription failed: {e}")
        raise Exception("Could not transcribe audio. Please try again.") from e


def clean_for_speech(text: str, lang: str = "en") -> str:
    """
    Clean text for speech synthesis by removing markdown, citations, etc.
    
    Args:
        text: Raw answer text from LLM
        lang: Language code ("en" or "te")
    
    Returns:
        Cleaned text suitable for TTS
    """
    if not text:
        return ""
    
    cleaned = text
    
    # Remove markdown headers
    cleaned = re.sub(r'^#{1,6}\s+', '', cleaned, flags=re.MULTILINE)
    
    # Remove bold/italic markers
    cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
    cleaned = re.sub(r'__([^_]+)__', r'\1', cleaned)
    cleaned = re.sub(r'_([^_]+)_', r'\1', cleaned)
    
    # Remove inline code
    cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
    
    # Remove code blocks
    cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)
    
    # Remove URLs
    cleaned = re.sub(r'https?://\S+', '', cleaned)
    
    # Remove citation markers like [Source: ...]
    cleaned = re.sub(r'\[Source[^\]]*\]', '', cleaned)
    
    # Remove "Sources:" section
    cleaned = re.sub(r'Sources?:.*$', '', cleaned, flags=re.MULTILINE | re.DOTALL)
    
    # Remove evidence/confidence line
    cleaned = re.sub(r'^Evidence:.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^Based on the loaded.*$', '', cleaned, flags=re.MULTILINE)
    
    # Remove bullet points but keep the text
    cleaned = re.sub(r'^[\s]*[-•*]\s+', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^[\s]*\d+\.\s+', '', cleaned, flags=re.MULTILINE)
    
    # Replace currency symbols with spoken words
    if lang == "te":
        cleaned = re.sub(r'Rs\.?\s*', 'రూపాయలు ', cleaned)
        cleaned = re.sub(r'₹\s*', 'రూపాయలు ', cleaned)
    else:
        cleaned = re.sub(r'Rs\.?\s*', 'rupees ', cleaned)
        cleaned = re.sub(r'₹\s*', 'rupees ', cleaned)
    
    # Collapse multiple whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    # Truncate to ~900 characters at sentence boundary
    if len(cleaned) > 900:
        # Find the last sentence boundary before 900
        truncated = cleaned[:900]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        last_boundary = max(last_period, last_exclamation, last_question)
        if last_boundary > 700:
            cleaned = cleaned[:last_boundary + 1]
        else:
            cleaned = cleaned[:900]
    
    return cleaned


def _run_edge_tts(text: str, voice: str) -> Optional[bytes]:
    """Run edge-tts in a separate thread to avoid event loop conflicts."""
    import edge_tts
    
    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_data = loop.run_until_complete(_generate())
        loop.close()
        return audio_data
    except Exception as e:
        logger.exception(f"edge-tts failed: {e}")
        return None


@st.cache_data(ttl=3600)
def synthesize(text: str, lang: str) -> Optional[bytes]:
    """
    Synthesize speech from text using edge-tts (primary) or gTTS (fallback).
    
    Args:
        text: Text to synthesize
        lang: Language code ("en" or "te")
    
    Returns:
        Audio bytes (MP3 format) or None if synthesis fails
    """
    if not text or len(text) < 2:
        return None
    
    # Select voice
    if lang == "te":
        edge_voice = "te-IN-ShrutiNeural"
        gtts_lang = "te"
    else:
        edge_voice = "en-IN-NeerjaNeural"
        gtts_lang = "en"
    
    # Try edge-tts first
    try:
        audio_data = _run_edge_tts(text, edge_voice)
        if audio_data:
            logger.info(f"TTS successful with edge-tts: {len(audio_data)} bytes")
            return audio_data
    except Exception as e:
        logger.warning(f"edge-tts failed: {type(e).__name__}")
    
    # Fallback to gTTS
    try:
        from gtts import gTTS
        
        tts = gTTS(text=text, lang=gtts_lang)
        audio_buffer = BytesIO()
        
        def _try_gtts():
            tts.write_to_fp(audio_buffer)
        
        thread = threading.Thread(target=_try_gtts)
        thread.start()
        thread.join(timeout=20)
        
        if thread.is_alive():
            logger.warning("gTTS timeout")
            thread.join(timeout=1)
        else:
            audio_buffer.seek(0)
            audio_data = audio_buffer.read()
            logger.info(f"TTS successful with gTTS: {len(audio_data)} bytes")
            return audio_data
            
    except Exception as e:
        logger.exception(f"gTTS failed: {e}")
    
    logger.warning("Both TTS methods failed")
    return None
