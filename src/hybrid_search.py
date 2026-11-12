
import json
import pickle
import re
import numpy as np
import faiss

from pathlib import Path
from sentence_transformers import SentenceTransformer, CrossEncoder


CHUNKS_PATH = Path("data/processed/chunks_v2.jsonl")
BM25_INDEX_PATH = Path("data/processed/bm25_index_v2.pkl")
BM25_CHUNKS_PATH = Path("data/processed/bm25_chunks_v2.jsonl")
FAISS_INDEX_PATH = Path("data/processed/agri_faiss_v2.index")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

RETRIEVAL_TOP_K = 50
RERANK_TOP_K = 50
FINAL_TOP_K = 4
RRF_K = 60


def tokenize(text):
    return re.findall(r"\w+", text.lower())


def load_jsonl(path):

    records = []

    with path.open("r", encoding="utf-8") as file:

        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def detect_requested_state(query, chunks):

    states = sorted(
        {chunk["state"] for chunk in chunks},
        key=len,
        reverse=True
    )

    query_lower = query.lower()

    for state in states:

        if state.lower() in query_lower:
            return state

    return None


def reciprocal_rank_fusion(rankings):

    rrf_scores = {}
    chunk_lookup = {}

    for ranking in rankings:

        for rank, chunk in enumerate(ranking, start=1):

            chunk_id = chunk["chunk_id"]

            score = 1 / (RRF_K + rank)

            rrf_scores[chunk_id] = (
                rrf_scores.get(chunk_id, 0) + score
            )

            chunk_lookup[chunk_id] = chunk

    ranked_chunk_ids = sorted(
        rrf_scores,
        key=lambda chunk_id: rrf_scores[chunk_id],
        reverse=True
    )

    return [
        {
            "chunk": chunk_lookup[chunk_id],
            "rrf_score": rrf_scores[chunk_id]
        }
        for chunk_id in ranked_chunk_ids[:RERANK_TOP_K]
    ]


def rerank_results(query, candidates, reranker):

    pairs = [
        [query, result["chunk"]["text"]]
        for result in candidates
    ]

    print("\nScoring passages using Cross-Encoder...")

    scores = reranker.predict(
        pairs,
        batch_size=16,
        show_progress_bar=True
    )

    for result, score in zip(candidates, scores):
        result["rerank_score"] = float(score)

    candidates.sort(
        key=lambda result: result["rerank_score"],
        reverse=True
    )

    return candidates[:FINAL_TOP_K]


def search(query):

    print("Loading chunks...")

    chunks = load_jsonl(CHUNKS_PATH)
    bm25_chunks = load_jsonl(BM25_CHUNKS_PATH)

    if len(chunks) != len(bm25_chunks):
        raise ValueError("Chunk counts do not match.")

    for a, b in zip(chunks, bm25_chunks):

        if a["chunk_id"] != b["chunk_id"]:
            raise ValueError("Chunk mappings do not match.")

    requested_state = detect_requested_state(query, chunks)

    if requested_state:

        print(f"\nState filter detected: {requested_state}")

        allowed_positions = [
            i for i, chunk in enumerate(chunks)
            if chunk["state"] == requested_state
        ]

    else:

        print("\nNo state filter detected. Searching all states.")

        allowed_positions = list(range(len(chunks)))

    if not allowed_positions:
        print("No chunks found for the requested state.")
        return

    print(f"Eligible chunks: {len(allowed_positions)}")

    print("\nLoading FAISS index...")

    faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))

    if faiss_index.ntotal != len(chunks):
        raise ValueError("FAISS index and chunk count do not match.")

    print("Loading BM25 index...")

    with BM25_INDEX_PATH.open("rb") as file:
        bm25 = pickle.load(file)

    print("Loading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL,
        device="cpu"
    )

    print("Loading Cross-Encoder model...")

    reranker = CrossEncoder(
        RERANKER_MODEL,
        device="cpu"
    )

    # 1. FAISS SEARCH WITH STATE FILTER

    print("\nPerforming FAISS search...")

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.ascontiguousarray(
        query_embedding,
        dtype=np.float32
    )

    # Search all vectors, then retain only eligible state positions.
    dense_scores, dense_indices = faiss_index.search(
        query_embedding,
        faiss_index.ntotal
    )

    dense_results = []

    for score, position in zip(
        dense_scores[0],
        dense_indices[0]
    ):

        if int(position) in allowed_positions:
            dense_results.append(chunks[int(position)])

            if len(dense_results) == RETRIEVAL_TOP_K:
                break

    # 2. BM25 SEARCH WITH STATE FILTER

    print("Performing BM25 search...")

    query_tokens = tokenize(query)
    sparse_scores = bm25.get_scores(query_tokens)

    allowed_scores = [
        (int(position), sparse_scores[position])
        for position in allowed_positions
    ]

    allowed_scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    sparse_results = [
        bm25_chunks[position]
        for position, score in allowed_scores[:RETRIEVAL_TOP_K]
    ]

    print(f"FAISS results: {len(dense_results)}")
    print(f"BM25 results: {len(sparse_results)}")

    # 3. RRF

    print("\nCombining rankings using RRF...")

    candidates = reciprocal_rank_fusion([
        dense_results,
        sparse_results
    ])

    print(f"Unique RRF candidates: {len(candidates)}")

    # 4. CROSS-ENCODER

    final_results = rerank_results(
        query,
        candidates,
        reranker
    )

    # 5. DISPLAY

    print("\nFINAL RERANKED RESULTS")
    print("=" * 70)

    for rank, result in enumerate(final_results, start=1):

        chunk = result["chunk"]

        print(f"\nRESULT {rank}")
        print("-" * 70)

        print(f"Cross-Encoder score: {result['rerank_score']:.6f}")
        print(f"Original RRF score: {result['rrf_score']:.6f}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"State: {chunk['state']}")
        print(f"PDF page: {chunk['pdf_page']}")
        print(f"Source: {chunk['source']}")

        print("\nRetrieved text:")
        print(chunk["text"])


def main():

    query = input(
        "\nEnter your agricultural question: "
    ).strip()

    if not query:
        print("Please enter a question.")
        return

    search(query)


if __name__ == "__main__":
    main()
