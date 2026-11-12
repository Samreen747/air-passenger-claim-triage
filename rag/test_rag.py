"""Basic dependency-free tests for chunking and retrieval formatting."""

import unittest
from unittest.mock import patch

from rag.chunking import chunk_pages
from rag.retrieval import retrieve_passages


class ChunkingTests(unittest.TestCase):
    def test_chunks_keep_provenance_and_overlap(self):
        result = chunk_pages([{
            "text": "abcdefghijklmnopqrstuvwxyz0123456789",
            "source": "regulation.pdf", "page": 4, "section": "Section 2",
        }], chunk_size=12, overlap=3)
        self.assertGreaterEqual(len(result), 2)
        self.assertTrue(all(item["source"] == "regulation.pdf" for item in result))
        self.assertTrue(all(item["page"] == 4 and item["section"] == "Section 2" for item in result))
        self.assertTrue(set(result[0]["text"]) & set(result[1]["text"]))


class RetrievalTests(unittest.TestCase):
    def test_passages_match_workflow_contract(self):
        class DummyEmbedder:
            def encode(self, texts):
                return [[0.1, 0.2]]

        class DummyStore:
            def search(self, vector, top_k):
                return [{"text": "Actual source text", "source": "DGCA.pdf", "page": 7,
                         "section": "Section 3", "score": 0.8}]

        with patch("rag.retrieval.SentenceTransformerEmbedder", DummyEmbedder), \
             patch("rag.retrieval._store", return_value=DummyStore()):
            result = retrieve_passages("flight delay")
        self.assertEqual(result, [{
            "text": "Actual source text", "citation": "DGCA.pdf, page 7, Section 3",
            "source": "DGCA.pdf", "page": 7, "section": "Section 3",
        }])


if __name__ == "__main__":
    unittest.main()
