"""Citation formatting and display helpers."""

from typing import List, Dict, Any


def format_citations(sources: List[Dict[str, Any]], language: str = "English") -> str:
    """Format source citations for display in Streamlit."""
    if not sources:
        return ""

    # Deduplicate sources
    seen = set()
    unique_sources = []
    for s in sources:
        key = f"{s.get('document', '')}_{s.get('page', '')}_{s.get('section', '')}"
        if key not in seen:
            seen.add(key)
            unique_sources.append(s)

    if language == "Telugu":
        header = "### 📚 మూలాలు (Sources)"
        confidence_labels = {
            "High": "అధిక నమ్మకత",
            "Medium": "మధ్యస్థ నమ్మకత",
            "Low": "పరిమిత నమ్మకత",
            "Insufficient": "తగినంత సాక్ష్యం లేదు"
        }
    else:
        header = "### 📚 Sources"
        confidence_labels = {
            "High": "High confidence",
            "Medium": "Medium confidence",
            "Low": "Limited confidence",
            "Insufficient": "Insufficient evidence"
        }

    lines = [header, ""]

    for s in unique_sources:
        doc = s.get("document", "Unknown document")
        page = s.get("page", "?")
        section = s.get("section", "")
        confidence = s.get("confidence", "")
        scheme = s.get("scheme_name", "")

        line = f"**{doc}**"
        if page:
            line += f", Page {page}"
        if section and section != "General":
            line += f" | *{section}*"
        if confidence:
            conf_label = confidence_labels.get(confidence, confidence)
            line += f" `{conf_label}`"

        lines.append(f"- {line}")

    lines.append("")
    if language == "Telugu":
        lines.append(
            "> 📌 *పై సమాచారం అధికారిక ప్రభుత్వ పత్రాల నుండి తీసుకోబడింది. "
            "CitizenAssist అందించే సమాచారం అధికారిక ప్రభుత్వ నిర్ణయం కాదు.*"
        )
    else:
        lines.append(
            "> 📌 *Information above is retrieved from official government documents. "
            "CitizenAssist's responses are not official government decisions.*"
        )

    return "\n".join(lines)


def format_confidence_badge(confidence: str, language: str = "English") -> str:
    """Format a confidence badge string."""
    badges = {
        "High": "Evidence: High, directly from the official document",
        "Medium": "Evidence: Medium, based on related sections",
        "Low": "Evidence: Low, based on a partial match",
        "Insufficient": "Evidence: Insufficient, please verify with the official source",
    }
    badges_te = {
        "High": "సాక్ష్యం: అధికం, నేరుగా అధికారిక పత్రం నుండి",
        "Medium": "సాక్ష్యం: మధ్యస్థం, సంబంధిత విభాగాల నుండి",
        "Low": "సాక్ష్యం: పరిమితం, పాక్షిక సరిపోలిక ఆధారంగా",
        "Insufficient": "సాక్ష్యం: తగినంత లేదు, అధికారిక మూలాన్ని ధృవీకరించండి",
    }
    if language == "Telugu":
        return badges_te.get(confidence, "")
    return badges.get(confidence, "")


def build_source_expandable(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build structured data for expandable source citations in Streamlit."""
    seen = set()
    result = []
    for s in sources:
        key = f"{s.get('document', '')}_{s.get('page', '')}_{s.get('section', '')}"
        if key not in seen:
            seen.add(key)
            result.append({
                "title": f"{s.get('document', 'Document')}, Page {s.get('page', '?')}",
                "section": s.get("section", "General"),
                "scheme": s.get("scheme_name", ""),
                "confidence": s.get("confidence", ""),
                "score": round(s.get("score", 0), 3)
            })
    return result
