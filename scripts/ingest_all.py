"""
CitizenAssist --- scripts/ingest_all.py
Run once to ingest all scheme PDFs and build the FAISS vector index.
Usage: python scripts/ingest_all.py
"""

import os
import sys
import json
import logging
from pathlib import Path

# Resolve every project file relative to the repository, not the launch folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from src.config import get_setting
from src.ingestion import VectorStore, EmbeddingEngine, ingest_all_pdfs

load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("  CitizenAssist - Document Ingestion Pipeline")
    print("=" * 60)

    # Paths
    schemes_dir = PROJECT_ROOT / "data" / "schemes"
    vectorstore_path = Path(get_setting("VECTORSTORE_PATH", "vectorstore"))
    if not vectorstore_path.is_absolute():
        vectorstore_path = PROJECT_ROOT / vectorstore_path
    schemes_config_path = PROJECT_ROOT / "schemes_config.json"

    # Check PDF directory
    if not schemes_dir.exists():
        print(f"\n[ERROR] PDFs directory not found: {schemes_dir}")
        print("Run first: python scripts/generate_sample_pdfs.py")
        sys.exit(1)

    pdfs = list(schemes_dir.glob("*.pdf"))
    if not pdfs:
        print(f"\n[ERROR] No PDF files found in {schemes_dir}")
        print("Run first: python scripts/generate_sample_pdfs.py")
        sys.exit(1)

    print(f"\n[INFO] Found {len(pdfs)} PDF files in {schemes_dir}")
    for p in pdfs:
        print(f"   - {p.name} ({p.stat().st_size // 1024} KB)")

    # Load schemes config
    with open(schemes_config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    schemes = config["schemes"]
    print(f"\n[INFO] Loaded {len(schemes)} scheme configurations")

    # Initialize components
    print("\n[INFO] Loading embedding model (all-MiniLM-L6-v2)...")
    embedding_model = get_setting("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_engine = EmbeddingEngine(embedding_model)
    embedding_engine.load()
    print("   Embedding model ready")

    vector_store = VectorStore(str(vectorstore_path))

    # Run ingestion
    print("\n[INFO] Starting PDF ingestion...")
    print("-" * 40)

    results = ingest_all_pdfs(
        str(schemes_dir),
        schemes,
        vector_store,
        embedding_engine
    )

    # Summary
    print("\n" + "=" * 60)
    print("  Ingestion Summary")
    print("=" * 60)
    total_chunks = 0
    for scheme_id, count in results.items():
        scheme_name = next((s["name"] for s in schemes if s["id"] == scheme_id), scheme_id)
        status = "[OK]" if count > 0 else "[WARN]"
        print(f"  {status} {scheme_name}: {count} chunks")
        total_chunks += count

    print(f"\n  Total chunks indexed: {total_chunks}")
    print(f"  Vector store saved to: {vectorstore_path.absolute()}")

    if total_chunks == 0:
        print("\n[WARN] No chunks were indexed. Check PDF paths and content.")
        sys.exit(1)
    else:
        print("\n[DONE] Ingestion complete! CitizenAssist is ready to use.")
        print("   Run: streamlit run app.py")


if __name__ == "__main__":
    main()
