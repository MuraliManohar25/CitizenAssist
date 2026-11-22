"""
CitizenAssist — src/eligibility.py
Personalized eligibility checker: collects user info, retrieves conditions, evaluates via LLM.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from src.retrieval import get_retrieval_engine
from src.rag import call_llm, load_prompt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Eligibility Evaluation
# ---------------------------------------------------------------------------

class EligibilityChecker:
    """Evaluates citizen eligibility against retrieved scheme conditions."""

    def __init__(self, vectorstore_path: str = "./vectorstore"):
        self.retrieval_engine = get_retrieval_engine(vectorstore_path)

    def check(
        self,
        scheme_id: str,
        scheme_name: str,
        user_info: Dict[str, Any],
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Evaluate eligibility for a scheme.

        Args:
            scheme_id: ID of the scheme
            scheme_name: Display name of the scheme
            user_info: Dict of field_key → user_value from the eligibility form
            language: "English" or "Telugu"

        Returns:
            Structured eligibility result dict
        """
        # 1. Retrieve eligibility conditions from the document
        results = self.retrieval_engine.search(
            query="eligibility criteria conditions requirements who can apply age income category qualification",
            scheme_id=scheme_id,
            k=6
        )

        context_string, sources = self.retrieval_engine.get_context_string(results, max_chars=3000)

        if not context_string:
            return self._insufficient_response(scheme_name, language)

        # 2. Format user info for the prompt
        user_info_str = "\n".join(
            f"- {key}: {value}"
            for key, value in user_info.items()
            if value is not None and str(value).strip()
        )

        # 3. Build and call the eligibility prompt
        prompt_template = load_prompt("eligibility_prompt.txt")
        prompt = prompt_template.format(
            eligibility_context=context_string,
            scheme_name=scheme_name,
            user_info=user_info_str,
            language=language
        )

        llm_response = call_llm(prompt, temperature=0.1)

        # 4. Parse the JSON response
        result = self._parse_eligibility_response(llm_response)
        result["sources"] = sources
        result["user_info"] = user_info
        result["scheme_name"] = scheme_name

        return result

    def _parse_eligibility_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON eligibility response from LLM."""
        try:
            # Try to extract JSON from the response
            response_stripped = response.strip()

            # Find JSON block
            start = response_stripped.find("{")
            end = response_stripped.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response_stripped[start:end]
                parsed = json.loads(json_str)
                if not isinstance(parsed, dict):
                    raise ValueError("Eligibility response must be a JSON object.")
                return self._normalise_response(parsed)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Could not parse eligibility JSON: {e}")

        # Fallback if JSON parsing fails
        return {
            "overall_status": "MORE_INFO_NEEDED",
            "overall_explanation": "We were unable to fully process your eligibility at this time. Please try again or consult the official scheme document.",
            "conditions": [],
            "why_explanation": {"passed_conditions": [], "failed_conditions": [], "unknown_conditions": ["Unable to retrieve eligibility conditions."]},
            "disclaimer": "CitizenAssist provides an informational assessment. Final eligibility is determined by the government authority.",
            "sources": []
        }

    def _normalise_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Constrain model output to the public result schema before rendering it."""
        valid_statuses = {"LIKELY_ELIGIBLE", "MORE_INFO_NEEDED", "LIKELY_NOT_ELIGIBLE"}
        overall_status = str(response.get("overall_status", "MORE_INFO_NEEDED"))
        if overall_status not in valid_statuses:
            overall_status = "MORE_INFO_NEEDED"

        conditions = response.get("conditions", [])
        if not isinstance(conditions, list):
            conditions = []
        cleaned_conditions = []
        for condition in conditions[:12]:
            if not isinstance(condition, dict):
                continue
            status = str(condition.get("status", "UNKNOWN"))
            if status not in {"PASS", "FAIL", "UNKNOWN", "NOT_FOUND"}:
                status = "UNKNOWN"
            cleaned_conditions.append({
                "condition_name": str(condition.get("condition_name", "Eligibility condition")),
                "condition_name_te": str(condition.get("condition_name_te", "")),
                "document_requirement": str(condition.get("document_requirement", "")),
                "user_value": str(condition.get("user_value", "")),
                "status": status,
                "explanation": str(condition.get("explanation", "")),
                "explanation_te": str(condition.get("explanation_te", "")),
            })

        why = response.get("why_explanation", {})
        if not isinstance(why, dict):
            why = {}

        def clean_list(key: str) -> List[str]:
            values = why.get(key, [])
            if not isinstance(values, list):
                return []
            return [str(value) for value in values[:8]]

        return {
            "overall_status": overall_status,
            "overall_explanation": str(response.get("overall_explanation", "")),
            "overall_explanation_te": str(response.get("overall_explanation_te", "")),
            "conditions": cleaned_conditions,
            "why_explanation": {
                "passed_conditions": clean_list("passed_conditions"),
                "failed_conditions": clean_list("failed_conditions"),
                "unknown_conditions": clean_list("unknown_conditions"),
            },
            "disclaimer": str(response.get("disclaimer", "")),
            "disclaimer_te": str(response.get("disclaimer_te", "")),
            "sources": [],
        }

    def _insufficient_response(self, scheme_name: str, language: str) -> Dict[str, Any]:
        """Return a response when insufficient data is found."""
        if language == "Telugu":
            msg = f"{scheme_name} కోసం అర్హత నిబంధనలు అందుబాటులో ఉన్న పత్రాల్లో తగినంతగా కనుగొనబడలేదు."
        else:
            msg = f"Eligibility conditions for {scheme_name} could not be found in the available documents."

        return {
            "overall_status": "MORE_INFO_NEEDED",
            "overall_explanation": msg,
            "conditions": [],
            "why_explanation": {
                "passed_conditions": [],
                "failed_conditions": [],
                "unknown_conditions": ["Eligibility conditions not available in the loaded documents."]
            },
            "disclaimer": "CitizenAssist provides informational guidance. Final eligibility is determined by the government authority.",
            "sources": []
        }


# ---------------------------------------------------------------------------
# Status Helpers
# ---------------------------------------------------------------------------

STATUS_CONFIG = {
    "LIKELY_ELIGIBLE": {
        "emoji": "🟢",
        "label": "Likely Eligible",
        "label_te": "అర్హత ఉన్నట్లు కనిపిస్తుంది",
        "color": "#22c55e",
        "bg_color": "#f0fdf4",
        "border_color": "#86efac"
    },
    "MORE_INFO_NEEDED": {
        "emoji": "🟡",
        "label": "More Information Required",
        "label_te": "మరింత సమాచారం అవసరం",
        "color": "#eab308",
        "bg_color": "#fefce8",
        "border_color": "#fde047"
    },
    "LIKELY_NOT_ELIGIBLE": {
        "emoji": "🔴",
        "label": "Likely Not Eligible",
        "label_te": "అర్హత లేనట్లు కనిపిస్తుంది",
        "color": "#ef4444",
        "bg_color": "#fef2f2",
        "border_color": "#fca5a5"
    }
}

CONDITION_STATUS_ICONS = {
    "PASS": "✅",
    "FAIL": "❌",
    "UNKNOWN": "⚠️",
    "NOT_FOUND": "❓"
}

CONDITION_STATUS_LABELS = {
    "PASS": "Satisfied",
    "FAIL": "Not Satisfied",
    "UNKNOWN": "Information Not Provided",
    "NOT_FOUND": "Not Specified in Document"
}


def get_status_config(status: str) -> Dict[str, str]:
    return STATUS_CONFIG.get(status, STATUS_CONFIG["MORE_INFO_NEEDED"])


def get_condition_icon(status: str) -> str:
    return CONDITION_STATUS_ICONS.get(status, "❓")


def get_condition_label(status: str) -> str:
    return CONDITION_STATUS_LABELS.get(status, "Unknown")


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_eligibility_checker: Optional[EligibilityChecker] = None

def get_eligibility_checker(vectorstore_path: str = "./vectorstore") -> EligibilityChecker:
    global _eligibility_checker
    if _eligibility_checker is None:
        _eligibility_checker = EligibilityChecker(vectorstore_path)
    return _eligibility_checker
