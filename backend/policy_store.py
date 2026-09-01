import json
import os

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from config import DATA_DIR, EMBEDDING_MODEL


class PolicyRetriever:
    """
    Retrieves the store-policy clause that best matches a dispute query.

    Embeds policy clauses with a HuggingFace sentence-transformers model
    (all-MiniLM-L6-v2) and searches them with a FAISS inner-product index.
    The model is downloaded from the HuggingFace Hub on first run and then
    cached locally (~90MB) — this requires internet access once; after
    that it works offline from the local cache.
    """

    def __init__(self):
        path = os.path.join(DATA_DIR, "policies.json")
        with open(path) as f:
            self.policies = json.load(f)

        try:
            self.model = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as exc:
            raise RuntimeError(
                "Couldn't load the policy embedding model "
                f"'{EMBEDDING_MODEL}'. It downloads from the HuggingFace "
                "Hub on first run, so this usually means there's no "
                "internet access right now. Connect to the internet and "
                "restart the backend — after the first successful run the "
                "model is cached locally and no further downloads are "
                "needed."
            ) from exc

        texts = [p["text"] for p in self.policies]
        embeddings = self.model.encode(texts, normalize_embeddings=True)

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(np.array(embeddings, dtype="float32"))

    def search(self, query: str, top_k: int = 1, expected_category: str | None = None):
        query_vec = self.model.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(np.array(query_vec, dtype="float32"), top_k)

        matches = []
        for score, idx in zip(scores[0], indices[0]):
            policy = self.policies[idx]
            raw_similarity = float(score)
            semantic_score = self._normalize_cosine(raw_similarity)
            category_score = self._category_alignment(policy.get("category"), expected_category)
            confidence = self._calibrate_confidence(semantic_score, category_score)
            matches.append({**policy, "similarity": raw_similarity, "confidence": confidence})

        best_confidence = matches[0]["confidence"] if matches else 0.0
        return matches, best_confidence

    @staticmethod
    def _normalize_cosine(score: float) -> float:
        # FAISS IP with normalized embeddings gives cosine similarity in [-1, 1].
        # We remap to [0, 1] so 0.0 means opposite and 1.0 means identical.
        return max(min((score + 1.0) / 2.0, 1.0), 0.0)

    @staticmethod
    def _category_alignment(policy_category: str | None, expected_category: str | None) -> float:
        if not expected_category:
            return 0.5
        if policy_category == expected_category:
            return 1.0

        # Cross-cutting clauses are still strong matches even when category differs.
        if policy_category in {"defective", "high_value"}:
            return 0.85
        if policy_category == "general":
            return 0.7
        return 0.3

    @staticmethod
    def _calibrate_confidence(semantic_score: float, category_score: float) -> float:
        combined = (semantic_score * 0.7) + (category_score * 0.3)
        return round(max(min(combined, 1.0), 0.0) * 100, 1)
