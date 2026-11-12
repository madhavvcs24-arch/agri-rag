
import json
import pickle
import re
import time

from pathlib import Path
from rank_bm25 import BM25Okapi


CHUNKS_PATH = Path("data/processed/chunks_v2.jsonl")
BM25_INDEX_PATH = Path("data/processed/bm25_index_v2.pkl")
BM25_CHUNKS_PATH = Path("data/processed/bm25_chunks_v2.jsonl")


def load_chunks():

    chunks = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def tokenize(text):
    """Convert text into lowercase word tokens."""

    return re.findall(r"\w+", text.lower())


def build_index():

    print("Loading chunks...")

    chunks = load_chunks()

    print(f"Total chunks loaded: {len(chunks)}")

    print("\nTokenizing chunks...")

    tokenized_chunks = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    print("Building BM25 index...")

    bm25 = BM25Okapi(tokenized_chunks)

    print("\nSaving BM25 index...")

    with BM25_INDEX_PATH.open("wb") as file:
        pickle.dump(bm25, file)

    # Save chunks in exactly the same order as the BM25 corpus.
    with BM25_CHUNKS_PATH.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("\nBM25 INDEX SUMMARY")
    print("=" * 45)
    print(f"Total documents indexed: {len(tokenized_chunks)}")
    print(f"Index saved at: {BM25_INDEX_PATH}")
    print(f"Chunk mapping saved at: {BM25_CHUNKS_PATH}")


def main():

    start_time = time.time()

    build_index()

    print(f"\nTime taken: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
