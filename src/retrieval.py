"""
CitizenAssist — src/retrieval.py
Vector search and context retrieval from FAISS store.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from src.ingestion import VectorStore, EmbeddingEngine, DocumentChunk

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Retrieval Engine
# ---------------------------------------------------------------------------

class RetrievalEngine:
    """Main retrieval engine for CitizenAssist RAG pipeline."""

    def __init__(self, vectorstore_path: str = "./vectorstore"):
        self.vectorstore_path = vectorstore_path
        self.vector_store = VectorStore(vectorstore_path)
        self.embedding_engine = EmbeddingEngine(
            os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        )
        self._loaded = False

    def load(self) -> bool:
        """Load the vector store from disk."""
        if not self._loaded:
            self._loaded = self.vector_store.load()
            if self._loaded:
                self.embedding_engine.load()
                logger.info("Retrieval engine loaded successfully")
            else:
                logger.warning("Vector store not found — please run ingestion first")
        return self._loaded

    def is_ready(self) -> bool:
        return self._loaded and len(self.vector_store.chunks) > 0

    def search(
        self,
        query: str,
        scheme_id: Optional[str] = None,
        k: int = 5,
        min_score: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks for a query.

        Args:
            query: User's question or query text
            scheme_id: Optional scheme to restrict search to
            k: Number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of result dicts with chunk, score, confidence
        """
        if not query or not query.strip() or k <= 0:
            return []
        if not self.load():
            return []

        # Embed the query
        query_embedding = self.embedding_engine.embed_one(query)

        # Search the vector store
        results = self.vector_store.search(query_embedding, k=k * 2, scheme_id=scheme_id)

        # Filter by minimum score
        results = [r for r in results if r["score"] >= min_score]

        # Deduplicate by chunk content (avoid near-identical chunks)
        results = deduplicate_results(results)

        return results[:k]

    def get_context_string(
        self,
        results: List[Dict[str, Any]],
        max_chars: int = 4000
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Build a context string from search results for LLM prompt injection.

        Returns:
            Tuple of (context_string, sources_list)
        """
        if not results:
            return "", []

        context_parts = []
        sources = []
        total_chars = 0

        for i, result in enumerate(results):
            chunk: DocumentChunk = result["chunk"]
            text = chunk.text.strip()

            if total_chars + len(text) > max_chars:
                # Truncate last chunk if needed
                remaining = max_chars - total_chars
                if remaining > 100:
                    text = text[:remaining] + "..."
                else:
                    break

            source_label = f"[Source {i+1}: {chunk.document_title}, Page {chunk.page_number}, Section: {chunk.section}]"
            context_parts.append(f"{source_label}\n{text}")
            total_chars += len(text)

            sources.append({
                "document": chunk.document_title,
                "scheme_name": chunk.scheme_name,
                "scheme_id": chunk.scheme_id,
                "page": chunk.page_number,
                "section": chunk.section,
                "source_file": chunk.source_file,
                "confidence": result["confidence"],
                "score": result["score"]
            })

        context_string = "\n\n---\n\n".join(context_parts)
        return context_string, sources

    def get_overall_confidence(self, results: List[Dict[str, Any]]) -> str:
        """Get overall evidence confidence from results."""
        if not results:
            return "Insufficient"
        top_score = results[0]["score"] if results else 0
        if top_score >= 0.70:
            return "High"
        elif top_score >= 0.40:
            return "Medium"
        elif top_score >= 0.20:
            return "Low"
        else:
            return "Insufficient"

    def get_indexed_schemes(self) -> List[str]:
        """Return list of scheme IDs currently indexed."""
        if not self.load():
            return []
        return self.vector_store.get_scheme_ids()

    def get_total_chunks(self) -> int:
        if not self.load():
            return 0
        return self.vector_store.get_chunk_count()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def deduplicate_results(results: List[Dict[str, Any]], similarity_threshold: float = 0.90) -> List[Dict[str, Any]]:
    """Remove near-duplicate chunks based on text similarity."""
    seen_texts = []
    deduped = []

    for result in results:
        chunk_text = result["chunk"].text.strip().lower()
        is_dup = False
        for seen in seen_texts:
            if jaccard_similarity(chunk_text, seen) > similarity_threshold:
                is_dup = True
                break
        if not is_dup:
            seen_texts.append(chunk_text)
            deduped.append(result)

    return deduped


def jaccard_similarity(text1: str, text2: str) -> float:
    """Simple Jaccard word overlap for deduplication."""
    words1 = set(text1.split())
    words2 = set(text2.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


# ---------------------------------------------------------------------------
# Singleton instance for app use
# ---------------------------------------------------------------------------

_retrieval_engines: Dict[str, RetrievalEngine] = {}

def get_retrieval_engine(vectorstore_path: str = "./vectorstore") -> RetrievalEngine:
    """Get a cached retrieval engine for the requested vector store."""
    store_key = str(Path(vectorstore_path).resolve())
    if store_key not in _retrieval_engines:
        engine = RetrievalEngine(store_key)
        engine.load()
        _retrieval_engines[store_key] = engine
    return _retrieval_engines[store_key]


def clear_retrieval_engines() -> None:
    """Clear process-local cached indexes after an intentional re-index."""
    _retrieval_engines.clear()
