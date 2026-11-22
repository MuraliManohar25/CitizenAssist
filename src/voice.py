"""
CitizenAssist — src/voice.py
Optional voice input/output (Speech-to-Text and Text-to-Speech).
Currently a stub — P1 feature.
"""

import logging

logger = logging.getLogger(__name__)


class VoiceEngine:
    """
    Voice interaction engine (stub).
    
    P1 feature: Implement using Google Cloud Speech-to-Text / Text-to-Speech
    or browser-based Web Speech API via streamlit-webrtc.
    """

    def __init__(self):
        self.available = False
        logger.info("Voice engine initialized (stub mode)")

    def speech_to_text(self, audio_data: bytes, language: str = "en-IN") -> str:
        """Convert speech audio to text."""
        logger.warning("Voice STT not yet implemented")
        return ""

    def text_to_speech(self, text: str, language: str = "en-IN") -> bytes:
        """Convert text to speech audio."""
        logger.warning("Voice TTS not yet implemented")
        return b""

    def is_available(self) -> bool:
        return self.available


def get_voice_engine() -> VoiceEngine:
    return VoiceEngine()
