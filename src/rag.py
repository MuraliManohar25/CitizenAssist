"""
CitizenAssist — src/rag.py
RAG pipeline: query → retrieve → prompt → LLM → structured response
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from dotenv import load_dotenv

from src.retrieval import RetrievalEngine, get_retrieval_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LLM Setup — supports both google-genai (new) and google-generativeai (old)
# ---------------------------------------------------------------------------

_llm_client = None
_llm_type = None  # "genai_new" or "genai_old"


class LLMServiceError(RuntimeError):
    """A safe application-level error for an unavailable model service."""

def setup_llm():
    """Configure Google Gemini API — tries new SDK first, falls back to old."""
    global _llm_client, _llm_type
    api_key = os.getenv("GOOGLE_API_KEY", "") or st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key or api_key == "your_google_api_key_here":
        raise LLMServiceError("The language model is not configured. Please set GOOGLE_API_KEY in .env or Streamlit secrets.")
    model_name = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")

    # Try new google-genai SDK first
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        _llm_client = (client, model_name)
        _llm_type = "genai_new"
        logger.info(f"Using google-genai (new SDK) with model: {model_name}")
        return _llm_client
    except ImportError:
        pass

    # Fall back to google-generativeai (old SDK)
    try:
        import google.generativeai as genai_old
        genai_old.configure(api_key=api_key)
        model = genai_old.GenerativeModel(model_name)
        _llm_client = model
        _llm_type = "genai_old"
        logger.info(f"Using google-generativeai (old SDK) with model: {model_name}")
        return _llm_client
    except ImportError:
        raise LLMServiceError("No supported Google AI client is installed.")


def get_llm():
    global _llm_client
    if _llm_client is None:
        setup_llm()
    return _llm_client


def call_llm(prompt: str, temperature: float = 0.3) -> str:
    """Call the configured LLM and return non-empty text.

    Provider details are logged server-side only. Callers receive a safe error that
    can be shown to citizens without exposing configuration or upstream internals.
    """
    try:
        get_llm()

        if _llm_type == "genai_new":
            from google import genai
            from google.genai import types
            client, model_name = _llm_client
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            text = getattr(response, "text", None)
            if not text:
                raise LLMServiceError("The language model returned an empty response.")
            return text

        else:  # genai_old
            import google.generativeai as genai_old
            response = _llm_client.generate_content(
                prompt,
                generation_config=genai_old.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            text = getattr(response, "text", None)
            if not text:
                raise LLMServiceError("The language model returned an empty response.")
            return text

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        if isinstance(e, LLMServiceError):
            raise
        raise LLMServiceError("The language model is temporarily unavailable.") from e


# ---------------------------------------------------------------------------
# Prompt Loading
# ---------------------------------------------------------------------------

def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    prompt_path = PROJECT_ROOT / "prompts" / prompt_name
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    logger.warning(f"Prompt file not found: {prompt_name}")
    return ""


# ---------------------------------------------------------------------------
# RAG Pipeline
# ---------------------------------------------------------------------------

class RAGPipeline:
    """Main RAG pipeline for CitizenAssist."""

    def __init__(self, vectorstore_path: str = "./vectorstore"):
        self.retrieval_engine = get_retrieval_engine(vectorstore_path)
        self.min_similarity = float(os.getenv("RAG_MIN_SIMILARITY", "0.20"))
        self.top_k = int(os.getenv("RAG_TOP_K", "5"))

    def answer(
        self,
        question: str,
        scheme_id: Optional[str] = None,
        scheme_name: str = "the selected scheme",
        language: str = "English",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        simple_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Full RAG answer pipeline.

        Returns:
            Dict with keys: answer, sources, confidence, retrieved_chunks, insufficient_evidence
        """
        # 1. Retrieve relevant content
        results = self.retrieval_engine.search(
            query=question,
            scheme_id=scheme_id,
            k=self.top_k,
            min_score=self.min_similarity
        )

        # 2. Build context
        context_string, sources = self.retrieval_engine.get_context_string(results)
        confidence = self.retrieval_engine.get_overall_confidence(results)

        # 3. Check if we have sufficient evidence
        insufficient = not results or confidence == "Insufficient"

        # 4. Build conversation history string
        history_str = ""
        if conversation_history:
            history_parts = []
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                role = "User" if msg.get("role") == "user" else "CitizenAssist"
                history_parts.append(f"{role}: {msg.get('content', '')[:200]}")
            history_str = "\n".join(history_parts)

        # 5. Build and call LLM prompt
        prompt_template = load_prompt("rag_prompt.txt")

        question_notes = []
        if simple_mode:
            question_notes.append("Use extremely simple language. Explain government terms in everyday words.")
        if language == "Telugu":
            question_notes.append("Respond entirely in Telugu script (తెలుగు).")
        question_augmented = question
        if question_notes:
            question_augmented = f"{question}\n\n[Response requirements: {' '.join(question_notes)}]"

        if insufficient:
            if language == "Telugu":
                answer = (
                    "మీరు అడిగిన ప్రశ్నకు అందుబాటులో ఉన్న అధికారిక పత్రాల్లో తగినంత సమాచారం దొరకలేదు. "
                    "తప్పుడు సమాచారం ఇవ్వకూడదనే ఉద్దేశ్యంతో ఈ విషయంలో అభిప్రాయం చెప్పలేదు. "
                    "దయచేసి అధికారిక వెబ్‌సైట్ లేదా సంబంధిత ప్రభుత్వ కార్యాలయాన్ని సంప్రదించండి."
                )
            else:
                answer = (
                    "The available official documents do not provide enough information to answer this question accurately. "
                    "I don't want to guess and give you incorrect information about government scheme rules.\n\n"
                    "Please verify this directly with the official source or the relevant government department."
                )
            return {
                "answer": answer,
                "sources": [],
                "confidence": "Insufficient",
                "retrieved_chunks": [],
                "insufficient_evidence": True
            }

        # Build the full prompt
        prompt = prompt_template.format(
            retrieved_context=context_string,
            user_question=question_augmented,
            scheme_name=scheme_name,
            language=language,
            conversation_history=history_str or "No prior conversation."
        )

        # 6. Call LLM
        llm_response = call_llm(prompt, temperature=0.3)

        return {
            "answer": llm_response,
            "sources": sources,
            "confidence": confidence,
            "retrieved_chunks": results,
            "insufficient_evidence": False
        }

    def get_simple_explanation(
        self,
        text: str,
        scheme_name: str,
        language: str = "English"
    ) -> str:
        """Generate a simple language explanation of a government text passage."""
        prompt_template = load_prompt("simple_explain_prompt.txt")
        prompt = prompt_template.format(
            original_text=text,
            scheme_name=scheme_name,
            language=language
        )
        return call_llm(prompt, temperature=0.4)

    def get_documents_and_steps(
        self,
        scheme_id: str,
        scheme_name: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Retrieve required documents and application steps for a scheme.
        """
        # Search for documents and procedure content
        docs_results = self.retrieval_engine.search(
            query="required documents needed to apply application procedure",
            scheme_id=scheme_id,
            k=5
        )
        steps_results = self.retrieval_engine.search(
            query="how to apply application process steps procedure portal",
            scheme_id=scheme_id,
            k=4
        )

        all_results = docs_results + steps_results
        context_string, sources = self.retrieval_engine.get_context_string(all_results, max_chars=3500)

        if not context_string:
            return {
                "documents": ["Please refer to the official scheme document for required documents."],
                "steps": ["Please refer to the official scheme document for application steps."],
                "sources": [],
                "insufficient": True
            }

        lang_note = "Respond entirely in Telugu script." if language == "Telugu" else ""

        prompt = f"""You are CitizenAssist. Based ONLY on the following official document content, provide:
1. A list of required documents citizens need to apply
2. Step-by-step application process

OFFICIAL CONTENT:
{context_string}

SCHEME: {scheme_name}
LANGUAGE: {language}
{lang_note}

RULES:
- Only list documents explicitly mentioned in the official content
- Only describe steps supported by the official content
- If the content is unclear about a step/document, say so
- Never invent information not in the content
- Use simple, clear language

RESPONSE FORMAT (use exactly this):

### 📄 Required Documents

[Numbered list of required documents from the official content]

### 🧭 Application Steps

[Numbered list of application steps from the official content]

### ⚠️ Important Notes

[Any important deadlines, conditions, or cautions from the content]

### 📚 Based On

[Document name and pages this information comes from]"""

        response = call_llm(prompt, temperature=0.2)
        return {
            "content": response,
            "sources": sources,
            "insufficient": False
        }

    def is_ready(self) -> bool:
        return self.retrieval_engine.is_ready()


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_rag_pipelines: Dict[str, RAGPipeline] = {}

def get_rag_pipeline(vectorstore_path: str = "./vectorstore") -> RAGPipeline:
    store_key = str(Path(vectorstore_path).resolve())
    if store_key not in _rag_pipelines:
        _rag_pipelines[store_key] = RAGPipeline(store_key)
    return _rag_pipelines[store_key]


def clear_rag_pipelines() -> None:
    """Clear cached pipelines after an intentional index rebuild."""
    _rag_pipelines.clear()
