
import json
import pickle
import re

from pathlib import Path


BM25_INDEX_PATH = Path("data/processed/bm25_index.pkl")
CHUNKS_PATH = Path("data/processed/bm25_chunks.jsonl")

TOP_K = 10


def tokenize(text):
    """Convert text into lowercase word tokens."""

    return re.findall(r"\w+", text.lower())


def load_chunks():

    chunks = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def search(query):

    print("Loading BM25 index...")

    with BM25_INDEX_PATH.open("rb") as file:
        bm25 = pickle.load(file)

    chunks = load_chunks()

    # Tokenize the farmer's question.
    query_tokens = tokenize(query)

    # Calculate relevance scores for all chunks.
    scores = bm25.get_scores(query_tokens)

    # Get positions of the highest-scoring chunks.
    ranked_indices = scores.argsort()[::-1][:TOP_K]

    print("\nBM25 SEARCH RESULTS")
    print("=" * 70)

    for rank, position in enumerate(ranked_indices, start=1):

        chunk = chunks[int(position)]
        score = scores[position]

        print(f"\nRESULT {rank}")
        print("-" * 70)

        print(f"BM25 score: {float(score):.4f}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"State: {chunk['state']}")
        print(f"PDF page: {chunk['pdf_page']}")
        print(f"Source: {chunk['source']}")

        print("\nRetrieved text:")
        print(chunk["text"])


def main():

    query = input("\nEnter your agricultural question: ").strip()

    if not query:
        print("Please enter a question.")
        return

    search(query)


if __name__ == "__main__":
    main()
