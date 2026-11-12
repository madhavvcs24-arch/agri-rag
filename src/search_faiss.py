
import json
import numpy as np
import faiss

from pathlib import Path
from sentence_transformers import SentenceTransformer


CHUNKS_PATH = Path("data/processed/chunks.jsonl")
INDEX_PATH = Path("data/processed/agri_faiss.index")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 10


def load_chunks():
    """Load original chunks and their metadata."""

    chunks = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def search(query):

    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    print("Loading FAISS index...")

    index = faiss.read_index(str(INDEX_PATH))

    chunks = load_chunks()

    # Convert the question into an embedding.
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.ascontiguousarray(
        query_embedding,
        dtype=np.float32
    )

    # Search all vectors.
    scores, indices = index.search(
        query_embedding,
        index.ntotal
    )

    # Filter results belonging to Karnataka.
    filtered_results = []

    for score, position in zip(scores[0], indices[0]):

        if position == -1:
            continue

        chunk = chunks[int(position)]

        if chunk["state"].lower() == "karnataka":
            filtered_results.append((score, chunk))

        if len(filtered_results) == TOP_K:
            break

    print("\nSEARCH RESULTS")
    print("=" * 70)

    # Print each result exactly once.
    for rank, (score, chunk) in enumerate(
        filtered_results,
        start=1
    ):

        print(f"\nRESULT {rank}")
        print("-" * 70)

        print(f"Similarity score: {float(score):.4f}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"State: {chunk['state']}")
        print(f"PDF page: {chunk['pdf_page']}")
        print(f"Source: {chunk['source']}")

        print("\nRetrieved text:")
        print(chunk["text"])

    if not filtered_results:
        print("No matching Karnataka passages found.")


def main():

    query = input("\nEnter your agricultural question: ").strip()

    if not query:
        print("Please enter a question.")
        return

    search(query)


if __name__ == "__main__":
    main()
