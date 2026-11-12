
import json
import re
from pathlib import Path

import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "indexes" / "faiss_index.bin"
METADATA_PATH = BASE_DIR / "indexes" / "chunks_metadata.json"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CANDIDATE_K = 30
RERANK_K = 20


# --------------------------------------------------
# TOKENIZATION
# --------------------------------------------------

def tokenize(text):
    """Convert text into lowercase word tokens."""
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


# --------------------------------------------------
# AGRICULTURAL RETRIEVER
# --------------------------------------------------

class AgriculturalRetriever:

    def __init__(self):
        print("Loading FAISS index...")

        self.index = faiss.read_index(str(INDEX_PATH))

        with open(METADATA_PATH, "r", encoding="utf-8") as file:
            metadata = json.load(file)

        self.chunks = metadata["chunks"]

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                "FAISS index and metadata counts do not match."
            )

        print(f"Loaded {len(self.chunks)} chunks.")

        print("\nLoading embedding model...")

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL,
            device="cpu"
        )

        print("\nBuilding BM25 index...")

        tokenized_documents = [
            tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

        print("BM25 index ready.")

        print("\nLoading Cross-Encoder...")

        self.reranker = CrossEncoder(
            RERANKER_MODEL,
            max_length=512,
            device="cpu"
        )

        print("\nAgricultural retriever is ready!")

    # --------------------------------------------------
    # METADATA FILTERING
    # --------------------------------------------------

    def get_allowed_positions(self, state=None, crop=None):
        """
        Return chunk positions matching optional state and crop filters.
        """

        allowed = []

        for position, chunk in enumerate(self.chunks):

            if state is not None:
                if (chunk.get("state") or "").casefold() != state.casefold():
                    continue

            if crop is not None:
                if (chunk.get("crop") or "").casefold() != crop.casefold():
                    continue

            allowed.append(position)

        return allowed

    # --------------------------------------------------
    # FAISS SEMANTIC SEARCH
    # --------------------------------------------------

    def semantic_search(self, query, allowed_positions):
        """Search the complete FAISS index, then apply metadata filters."""

        query_vector = self.embedding_model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        scores, indices = self.index.search(
            query_vector.astype("float32"),
            self.index.ntotal
        )

        allowed_set = set(allowed_positions)
        results = []

        for score, position in zip(scores[0], indices[0]):

            if position not in allowed_set:
                continue

            results.append({
                "position": int(position),
                "score": float(score)
            })

            if len(results) >= CANDIDATE_K:
                break

        return results

    # --------------------------------------------------
    # BM25 KEYWORD SEARCH
    # --------------------------------------------------

    def keyword_search(self, query, allowed_positions):
        """Search the complete BM25 corpus, then apply metadata filters."""

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        results = []

        for position in allowed_positions:
            results.append({
                "position": position,
                "score": float(scores[position])
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:CANDIDATE_K]

    # --------------------------------------------------
    # RECIPROCAL RANK FUSION
    # --------------------------------------------------

    @staticmethod
    def reciprocal_rank_fusion(
        semantic_results,
        keyword_results,
        constant=60
    ):
        """Combine semantic and keyword rankings."""

        fused_scores = {}

        for results in [semantic_results, keyword_results]:

            for rank, result in enumerate(results, start=1):

                position = result["position"]

                if position not in fused_scores:
                    fused_scores[position] = 0.0

                fused_scores[position] += (
                    1.0 / (constant + rank)
                )

        ranked = sorted(
            fused_scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return [
            {
                "position": position,
                "rrf_score": score
            }
            for position, score in ranked
        ]

    # --------------------------------------------------
    # CROSS-ENCODER RERANKING
    # --------------------------------------------------

    def rerank(self, query, fused_results):

        candidates = fused_results[:RERANK_K]

        pairs = []

        for result in candidates:
            chunk = self.chunks[result["position"]]

            pairs.append([
                query,
                chunk["text"]
            ])

        if not pairs:
            return []

        scores = self.reranker.predict(
            pairs,
            show_progress_bar=False
        )

        reranked = []

        for result, score in zip(candidates, scores):

            position = result["position"]
            chunk = self.chunks[position]

            reranked.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "source": chunk["source"],
                "state": chunk["state"],
                "crop": chunk["crop"],
                "pdf_page": chunk["pdf_page"],
                "printed_page": chunk["printed_page"],
                "rrf_score": result["rrf_score"],
                "reranker_score": float(score)
            })

        reranked.sort(
            key=lambda item: item["reranker_score"],
            reverse=True
        )

        return reranked

    # --------------------------------------------------
    # MAIN SEARCH METHOD
    # --------------------------------------------------

    def search(self, query, state=None, crop=None, top_k=5):

        if not query or not query.strip():
            raise ValueError("Please provide a non-empty question.")

        allowed_positions = self.get_allowed_positions(
            state=state,
            crop=crop
        )

        if not allowed_positions:
            return []

        semantic_results = self.semantic_search(
            query,
            allowed_positions
        )

        keyword_results = self.keyword_search(
            query,
            allowed_positions
        )

        fused_results = self.reciprocal_rank_fusion(
            semantic_results,
            keyword_results
        )

        final_results = self.rerank(
            query,
            fused_results
        )

        return final_results[:top_k]
