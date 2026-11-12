
import json
import time
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("data/processed/chunks_v2.jsonl")
EMBEDDINGS_PATH = Path("data/processed/embeddings_v2.npy")
CHUNK_IDS_PATH = Path("data/processed/embedding_chunk_ids_v2.npy")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32

def load_chunks():
    """Load all previously generated text chunks."""

    chunks = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                chunks.append(json.loads(line))

    return chunks

def generate_embeddings(chunks):

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    texts = [chunk["text"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings

def save_embeddings(embeddings, chunks):

    np.save(EMBEDDINGS_PATH, embeddings)

    chunk_ids = np.array(
        [chunk["chunk_id"] for chunk in chunks],
        dtype=np.int32
    )

    np.save(CHUNK_IDS_PATH, chunk_ids)

def main():

    start_time = time.time()

    print("Loading chunks...")

    chunks = load_chunks()

    print(f"Total chunks: {len(chunks)}")

    embeddings = generate_embeddings(chunks)

    print("\nSaving embeddings...")

    save_embeddings(embeddings, chunks)

    print("\nEMBEDDING SUMMARY")
    print("=" * 45)

    print(f"Number of chunks: {embeddings.shape[0]}")
    print(f"Vector dimensions: {embeddings.shape[1]}")
    print(f"Data type: {embeddings.dtype}")
    print(f"Normalized vectors: True")

    print(f"\nEmbedding file: {EMBEDDINGS_PATH}")
    print(f"Chunk ID file: {CHUNK_IDS_PATH}")

    print(f"\nTime taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()