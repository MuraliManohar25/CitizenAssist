"""
CitizenAssist — src/ingestion.py
PDF ingestion pipeline: PDF → Text → Chunks → Embeddings → FAISS Index
"""

import os
import json
import pickle
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

import pymupdf as fitz  # PyMuPDF (use pymupdf to avoid deprecation warning)
import numpy as np
from sentence_transformers import SentenceTransformer
import streamlit as st

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class DocumentChunk:
    """A single chunk of text from a government document."""
    chunk_id: str
    text: str
    scheme_id: str
    scheme_name: str
    department: str
    state: str
    source_file: str
    document_title: str
    year: str
    page_number: int
    section: str
    chunk_index: int
    total_chunks: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Text Extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract text page by page from a PDF file."""
    pages = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            text = clean_text(text)
            if text.strip():
                pages.append({
                    "page_number": page_num + 1,
                    "text": text
                })
        doc.close()
        logger.info(f"Extracted {len(pages)} pages from {pdf_path}")
    except Exception as e:
        logger.error(f"Error extracting PDF {pdf_path}: {e}")
    return pages


def clean_text(text: str) -> str:
    """Clean extracted PDF text."""
    import re
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Remove common PDF artifacts
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # Page numbers alone
    text = text.strip()
    return text


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, page_number: int, chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, Any]]:
    """Split text into overlapping chunks by words."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_text.strip()) > 50:  # Skip very short chunks
            # Try to detect section heading
            section = detect_section(chunk_text)
            chunks.append({
                "text": chunk_text,
                "page_number": page_number,
                "section": section
            })

        if end == len(words):
            break
        start = end - overlap

    return chunks


def detect_section(text: str) -> str:
    """Heuristically detect section name from chunk text."""
    import re
    lines = text.strip().split('\n')
    for line in lines[:3]:
        line = line.strip()
        # Look for numbered sections or capitalized headings
        if re.match(r'^(\d+\.|\d+\.\d+|[A-Z][A-Z\s]{5,})', line) and len(line) < 100:
            return line[:80]
    return "General"


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

@st.cache_resource
def get_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """Load and cache the embedding model."""
    logger.info(f"Loading embedding model: {model_name}")
    try:
        model = SentenceTransformer(model_name, local_files_only=True)
    except OSError:
        logger.info("Embedding model is not cached locally; downloading it once.")
        model = SentenceTransformer(model_name)
    return model

class EmbeddingEngine:
    """Lightweight sentence embedding engine."""

    _instance = None

    def __new__(cls, model_name: str = "all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model_name = model_name
            cls._instance.model = None
        return cls._instance

    def load(self):
        if self.model is None:
            self.model = get_embedding_model(self.model_name)
        return self

    def embed(self, texts: List[str]) -> np.ndarray:
        self.load()
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def embed_one(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


# ---------------------------------------------------------------------------
# FAISS Index Management
# ---------------------------------------------------------------------------

class VectorStore:
    """FAISS-based vector store for document chunks."""

    def __init__(self, store_path: str = "./vectorstore"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.store_path / "faiss.index"
        self.chunks_file = self.store_path / "chunks.json"
        self.meta_file = self.store_path / "meta.pkl"

        self.index = None
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: np.ndarray):
        """Add chunks and normalized embeddings to the store."""
        import faiss

        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError("Each document chunk must have exactly one embedding.")

        new_embeddings = np.ascontiguousarray(embeddings.astype("float32", copy=True))
        dim = new_embeddings.shape[1]

        # IndexFlatIP is cosine similarity only when every vector is normalized.
        faiss.normalize_L2(new_embeddings)

        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)  # Inner product (cosine if normalized)
            self.embeddings = new_embeddings.copy()
        else:
            if self.index.d != dim:
                raise ValueError(
                    f"Embedding dimension {dim} does not match the existing index dimension {self.index.d}."
                )
            if self.embeddings is None:
                self.embeddings = self.index.reconstruct_n(0, self.index.ntotal)
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        self.index.add(new_embeddings)
        self.chunks.extend(chunks)
        logger.info(f"Added {len(chunks)} chunks. Total: {len(self.chunks)}")

    def save(self):
        """Persist the index and chunks to disk."""
        import faiss
        if self.index is None:
            return

        # Write complete temporary files before replacing the live index. This avoids
        # leaving a half-written knowledge base if indexing is interrupted.
        index_temp = self.index_file.with_suffix(".index.tmp")
        chunks_temp = self.chunks_file.with_suffix(".json.tmp")
        meta_temp = self.meta_file.with_suffix(".pkl.tmp")
        faiss.write_index(self.index, str(index_temp))
        with open(chunks_temp, "w", encoding="utf-8") as file:
            json.dump([chunk.to_dict() for chunk in self.chunks], file, ensure_ascii=False, indent=2, encoding="utf-8")
        with open(meta_temp, "wb") as file:
            pickle.dump({"embeddings": self.embeddings}, file)

        os.replace(index_temp, self.index_file)
        os.replace(chunks_temp, self.chunks_file)
        os.replace(meta_temp, self.meta_file)
        logger.info(f"Vector store saved: {len(self.chunks)} chunks")

    def load(self) -> bool:
        """Load persisted index from disk."""
        import faiss
        if not all(path.exists() for path in (self.index_file, self.chunks_file)):
            return False
        try:
            self.index = faiss.read_index(str(self.index_file))
            with open(self.chunks_file, "r", encoding="utf-8") as f:
                data = json.load(f, encoding="utf-8")
                self.chunks = [DocumentChunk(**d) for d in data]
            
            # Index consistency check
            if self.index.ntotal != len(self.chunks):
                raise ValueError(
                    f"Index has {self.index.ntotal} vectors but metadata has {len(self.chunks)} chunks. "
                    f"Please re-run ingestion: python scripts/ingest_all.py"
                )
            
            if self.meta_file.exists():
                with open(self.meta_file, "rb") as f:
                    meta = pickle.load(f)
                    self.embeddings = meta.get("embeddings")
            if self.embeddings is None or len(self.embeddings) != len(self.chunks):
                self.embeddings = self.index.reconstruct_n(0, self.index.ntotal)
            logger.info(f"Vector store loaded: {len(self.chunks)} chunks")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False

    def search(self, query_embedding: np.ndarray, k: int = 5, scheme_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        import faiss
        if self.index is None or len(self.chunks) == 0:
            return []

        query = np.ascontiguousarray(query_embedding.astype("float32").reshape(1, -1))
        if query.shape[1] != self.index.d:
            raise ValueError(
                f"Query embedding dimension {query.shape[1]} does not match index dimension {self.index.d}."
            )
        faiss.normalize_L2(query)

        # FAISS ranks globally. When a scheme filter is active, request every
        # candidate so a relevant chunk is not discarded just because unrelated
        # schemes occupy the first global results.
        search_k = len(self.chunks) if scheme_id else min(k * 2, len(self.chunks))
        scores, indices = self.index.search(query, search_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            if scheme_id and chunk.scheme_id != scheme_id:
                continue
            results.append({
                "chunk": chunk,
                "score": float(score),
                "confidence": score_to_confidence(float(score))
            })
            if len(results) >= k:
                break

        return results

    def get_scheme_ids(self) -> List[str]:
        """Get all unique scheme IDs in the store."""
        return sorted({chunk.scheme_id for chunk in self.chunks})

    def get_chunk_count(self, scheme_id: Optional[str] = None) -> int:
        if scheme_id:
            return sum(1 for c in self.chunks if c.scheme_id == scheme_id)
        return len(self.chunks)


def score_to_confidence(score: float) -> str:
    """Convert cosine similarity score to human-readable confidence."""
    if score >= 0.75:
        return "High"
    elif score >= 0.50:
        return "Medium"
    elif score >= 0.30:
        return "Low"
    else:
        return "Very Low"


# ---------------------------------------------------------------------------
# Main Ingestion Pipeline
# ---------------------------------------------------------------------------

def ingest_pdf(
    pdf_path: str,
    scheme_meta: Dict[str, Any],
    vector_store: VectorStore,
    embedding_engine: EmbeddingEngine,
    chunk_size: int = 500,
    overlap: int = 100
) -> int:
    """Full pipeline: PDF → chunks → embeddings → vector store."""
    logger.info(f"Ingesting: {pdf_path}")

    # 1. Extract text
    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        logger.warning(f"No text extracted from {pdf_path}")
        return 0

    # 2. Chunk text
    all_raw_chunks = []
    for page_data in pages:
        raw_chunks = chunk_text(page_data["text"], page_data["page_number"], chunk_size, overlap)
        all_raw_chunks.extend(raw_chunks)

    if not all_raw_chunks:
        return 0

    # 3. Build DocumentChunk objects
    source_filename = Path(pdf_path).name
    doc_chunks = []
    for i, raw in enumerate(all_raw_chunks):
        chunk_id = hashlib.md5(f"{scheme_meta['id']}_{i}_{raw['text'][:50]}".encode()).hexdigest()[:12]
        chunk = DocumentChunk(
            chunk_id=chunk_id,
            text=raw["text"],
            scheme_id=scheme_meta["id"],
            scheme_name=scheme_meta["name"],
            department=scheme_meta.get("department", ""),
            state=scheme_meta.get("state", ""),
            source_file=source_filename,
            document_title=scheme_meta.get("name", source_filename),
            year=scheme_meta.get("year", ""),
            page_number=raw["page_number"],
            section=raw["section"],
            chunk_index=i,
            total_chunks=len(all_raw_chunks)
        )
        doc_chunks.append(chunk)

    # 4. Generate embeddings
    texts = [c.text for c in doc_chunks]
    embeddings = embedding_engine.embed(texts)

    # 5. Add to vector store
    vector_store.add_chunks(doc_chunks, embeddings)

    logger.info(f"Ingested {len(doc_chunks)} chunks from {source_filename}")
    return len(doc_chunks)


def ingest_all_pdfs(
    schemes_dir: str,
    schemes_config: List[Dict[str, Any]],
    vector_store: VectorStore,
    embedding_engine: EmbeddingEngine
) -> Dict[str, int]:
    """Ingest all scheme PDFs listed in schemes_config."""
    results = {}
    schemes_path = Path(schemes_dir)

    for scheme in schemes_config:
        pdf_file = scheme.get("pdf_file", "")
        pdf_path = schemes_path / pdf_file

        if not pdf_path.exists():
            logger.warning(f"PDF not found: {pdf_path}")
            results[scheme["id"]] = 0
            continue

        count = ingest_pdf(str(pdf_path), scheme, vector_store, embedding_engine)
        results[scheme["id"]] = count

    vector_store.save()
    return results
