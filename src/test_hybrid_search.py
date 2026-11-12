
import json
import re
from pathlib import Path

import faiss
import numpy as np

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INDEX_PATH = PROJECT_ROOT / "indexes" / "faiss_index.bin"
METADATA_PATH = PROJECT_ROOT / "indexes" / "chunks_metadata.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5
RRF_CONSTANT = 60


# --------------------------------------------------
# 2. TOKENIZATION FOR BM25
# --------------------------------------------------

def tokenize(text):

    return re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )


# --------------------------------------------------
# 3. LOAD INDEX, METADATA AND MODEL
# --------------------------------------------------

def load_resources():

    print("Loading FAISS index...")

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    chunks = metadata["chunks"]

    if index.ntotal != len(chunks):
        raise ValueError("Index and metadata sizes do not match.")

    print(f"Chunks loaded: {len(chunks)}")

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    return index, chunks, model


# --------------------------------------------------
# 4. FILTER CHUNKS BY STATE AND CROP
# --------------------------------------------------

def filter_chunks(chunks, required_state, required_crop):

    matching = []

    for position, chunk in enumerate(chunks):

        state_matches = (
            chunk["state"].casefold() == required_state.casefold()
        )

        crop_matches = (
            (chunk["crop"] or "").casefold() == required_crop.casefold()
        )

        if state_matches and crop_matches:

            matching.append(
                {
                    "position": position,
                    "chunk": chunk
                }
            )

    return matching


# --------------------------------------------------
# 5. FAISS SEMANTIC RANKING
# --------------------------------------------------

def semantic_search(query, model, index, chunks, matching):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    scores, indices = index.search(
        query_embedding,
        index.ntotal
    )

    matching_positions = {
        item["position"]
        for item in matching
    }

    ranked = []

    for score, idx in zip(scores[0], indices[0]):

        if idx in matching_positions:

            ranked.append(
                {
                    "position": int(idx),
                    "score": float(score)
                }
            )

    return ranked


# --------------------------------------------------
# 6. BM25 KEYWORD RANKING
# --------------------------------------------------

def keyword_search(query, matching):

    documents = [
        tokenize(item["chunk"]["text"])
        for item in matching
    ]

    bm25 = BM25Okapi(documents)

    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    ranked = []

    for local_position, score in enumerate(scores):

        ranked.append(
            {
                "position": matching[local_position]["position"],
                "score": float(score)
            }
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return ranked


# --------------------------------------------------
# 7. RECIPROCAL RANK FUSION
# --------------------------------------------------

def reciprocal_rank_fusion(semantic_results, keyword_results):

    rrf_scores = {}

    rankings = [
        semantic_results,
        keyword_results
    ]

    for ranking in rankings:

        for rank, result in enumerate(ranking, start=1):

            position = result["position"]

            contribution = 1 / (
                RRF_CONSTANT + rank
            )

            rrf_scores[position] = (
                rrf_scores.get(position, 0) + contribution
            )

    fused_results = [
        {
            "position": position,
            "rrf_score": score
        }
        for position, score in rrf_scores.items()
    ]

    fused_results.sort(
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    return fused_results


# --------------------------------------------------
# 8. DISPLAY RESULTS
# --------------------------------------------------

def display_results(title, results, chunks, score_name):

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    for rank, result in enumerate(results[:TOP_K], start=1):

        chunk = chunks[result["position"]]

        print(f"\nRANK: {rank}")
        print(f"CHUNK ID: {chunk['chunk_id']}")
        print(f"STATE: {chunk['state']}")
        print(f"CROP: {chunk['crop']}")
        print(f"PDF PAGE: {chunk['pdf_page']}")
        print(f"{score_name}: {result[score_name]}")

        print("\nTEXT:")
        print(chunk["text"])

        print("-" * 80)


# --------------------------------------------------
# 9. MAIN
# --------------------------------------------------

def main():

    query = "How can I control weeds in paddy fields in Karnataka?"

    required_state = "Karnataka"
    required_crop = "Paddy"

    print("=" * 80)
    print("AGRICULTURAL RAG - HYBRID RETRIEVAL TEST")
    print("=" * 80)

    index, chunks, model = load_resources()

    matching = filter_chunks(
        chunks,
        required_state,
        required_crop
    )

    print(f"\nMatching state/crop chunks: {len(matching)}")

    if not matching:
        print("No matching chunks found.")
        return

    # Semantic retrieval
    semantic_results = semantic_search(
        query,
        model,
        index,
        chunks,
        matching
    )

    # Keyword retrieval
    keyword_results = keyword_search(
        query,
        matching
    )

    # Combine both rankings
    fused_results = reciprocal_rank_fusion(
        semantic_results,
        keyword_results
    )

    # Display individual and combined rankings
    display_results(
        "FAISS SEMANTIC RESULTS",
        semantic_results,
        chunks,
        "score"
    )

    display_results(
        "BM25 KEYWORD RESULTS",
        keyword_results,
        chunks,
        "score"
    )

    display_results(
        "RRF HYBRID RESULTS",
        fused_results,
        chunks,
        "rrf_score"
    )


if __name__ == "__main__":
    main()
