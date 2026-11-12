
import json
import re
from pathlib import Path

import faiss
import numpy as np
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

TOP_K = 5
CANDIDATE_K = 10
RRF_CONSTANT = 60

QUERY = "What seed rate is recommended for paddy cultivation in Karnataka?"

REQUIRED_STATE = "Karnataka"
REQUIRED_CROP = "Paddy"


# --------------------------------------------------
# TOKENIZATION
# --------------------------------------------------

def tokenize(text):
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


# --------------------------------------------------
# LOAD RESOURCES
# --------------------------------------------------

def load_resources():
    print("Loading FAISS index...")

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    chunks = metadata["chunks"]

    if index.ntotal != len(chunks):
        raise ValueError("FAISS index and metadata counts do not match.")

    print(f"Chunks loaded: {len(chunks)}")

    print("\nLoading embedding model...")

    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    print("\nLoading Cross-Encoder model...")

    reranker = CrossEncoder(
        RERANKER_MODEL,
        max_length=512,
        device="cpu"
    )

    return index, chunks, embedding_model, reranker


# --------------------------------------------------
# FILTER BY STATE AND CROP
# --------------------------------------------------

def filter_chunks(chunks):
    positions = []

    for position, chunk in enumerate(chunks):
        if (
            chunk.get("state") == REQUIRED_STATE
            and chunk.get("crop") == REQUIRED_CROP
        ):
            positions.append(position)

    return positions


# --------------------------------------------------
# FAISS SEMANTIC SEARCH
# --------------------------------------------------

def semantic_search(index, chunks, model, positions):
    query_vector = model.encode(
        [QUERY],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    scores, indices = index.search(
        query_vector.astype("float32"),
        index.ntotal
    )

    results = []

    for score, position in zip(scores[0], indices[0]):
        if position in positions:
            results.append({
                "position": int(position),
                "score": float(score)
            })

            if len(results) == CANDIDATE_K:
                break

    return results


# --------------------------------------------------
# BM25 KEYWORD SEARCH
# --------------------------------------------------

def keyword_search(chunks, positions):
    documents = [
        tokenize(chunks[position]["text"])
        for position in positions
    ]

    bm25 = BM25Okapi(documents)

    query_tokens = tokenize(QUERY)
    scores = bm25.get_scores(query_tokens)

    results = []

    for local_position, score in enumerate(scores):
        results.append({
            "position": positions[local_position],
            "score": float(score)
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:CANDIDATE_K]


# --------------------------------------------------
# RECIPROCAL RANK FUSION
# --------------------------------------------------

def reciprocal_rank_fusion(semantic_results, keyword_results):
    fused_scores = {}

    for results in [semantic_results, keyword_results]:
        for rank, result in enumerate(results, start=1):
            position = result["position"]

            if position not in fused_scores:
                fused_scores[position] = 0.0

            fused_scores[position] += (
                1.0 / (RRF_CONSTANT + rank)
            )

    ranked = sorted(
        fused_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return [
        {
            "position": position,
            "score": score
        }
        for position, score in ranked
    ]


# --------------------------------------------------
# CROSS-ENCODER RERANKING
# --------------------------------------------------

def rerank_candidates(chunks, fused_results, reranker):
    pairs = []

    for result in fused_results:
        chunk = chunks[result["position"]]

        pairs.append([
            QUERY,
            chunk["text"]
        ])

    print("\nScoring candidates with Cross-Encoder...")

    scores = reranker.predict(
        pairs,
        show_progress_bar=False
    )

    reranked = []

    for result, score in zip(fused_results, scores):
        reranked.append({
            "position": result["position"],
            "score": float(score)
        })

    reranked.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return reranked


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

def display_results(title, results, chunks):
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
        print(f"SCORE: {result['score']}")

        print("\nTEXT:")
        print(chunk["text"])

        print("-" * 80)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    print("=" * 80)
    print("AGRICULTURAL RAG - CROSS-ENCODER RERANKING TEST")
    print("=" * 80)

    index, chunks, embedding_model, reranker = load_resources()

    positions = filter_chunks(chunks)

    print(f"\nMatching state/crop chunks: {len(positions)}")

    if not positions:
        print("No matching chunks found.")
        return

    semantic_results = semantic_search(
        index,
        chunks,
        embedding_model,
        positions
    )

    keyword_results = keyword_search(
        chunks,
        positions
    )

    fused_results = reciprocal_rank_fusion(
        semantic_results,
        keyword_results
    )

    display_results(
        "RRF RESULTS BEFORE RERANKING",
        fused_results,
        chunks
    )

    reranked_results = rerank_candidates(
        chunks,
        fused_results,
        reranker
    )

    display_results(
        "CROSS-ENCODER RESULTS AFTER RERANKING",
        reranked_results,
        chunks
    )

    print("\nExperiment completed successfully.")


if __name__ == "__main__":
    main()
