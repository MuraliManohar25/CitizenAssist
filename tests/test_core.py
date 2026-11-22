"""Regression tests for the safe, non-network CitizenAssist core."""

from __future__ import annotations

import tempfile
import unittest

import numpy as np

from src.eligibility import EligibilityChecker
from src.ingestion import DocumentChunk, VectorStore


def make_chunk(chunk_id: str, scheme_id: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        text=f"Source text for {scheme_id}",
        scheme_id=scheme_id,
        scheme_name=scheme_id,
        department="Department",
        state="India",
        source_file="source.pdf",
        document_title="Source document",
        year="2026",
        page_number=1,
        section="General",
        chunk_index=0,
        total_chunks=1,
    )


class VectorStoreTests(unittest.TestCase):
    def test_scheme_filter_considers_all_global_candidates(self) -> None:
        """A filtered result must not disappear behind unrelated global results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(temp_dir)
            other_chunks = [make_chunk(f"other-{index}", "other") for index in range(10)]
            target_chunk = make_chunk("target", "target")
            chunks = other_chunks + [target_chunk]
            embeddings = np.array([[1.0, 0.0]] * 10 + [[0.9, 0.1]], dtype="float32")
            store.add_chunks(chunks, embeddings)

            results = store.search(
                np.array([1.0, 0.0], dtype="float32"),
                k=1,
                scheme_id="target",
            )

            self.assertEqual([item["chunk"].scheme_id for item in results], ["target"])


class EligibilityParsingTests(unittest.TestCase):
    def test_invalid_model_status_is_normalised(self) -> None:
        checker = EligibilityChecker.__new__(EligibilityChecker)
        result = checker._parse_eligibility_response(
            '{"overall_status":"INVALID","conditions":[{"condition_name":"Age","status":"PASS"},{"status":"NOPE"}]}'
        )

        self.assertEqual(result["overall_status"], "MORE_INFO_NEEDED")
        self.assertEqual(result["conditions"][0]["status"], "PASS")
        self.assertEqual(result["conditions"][1]["status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
