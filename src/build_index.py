
import json
import time
from pathlib import Path

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. PROJECT PATHS AND CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks_v2.jsonl"

INDEX_DIR = PROJECT_ROOT / "indexes"

FAISS_PATH = INDEX_DIR / "faiss_index.bin"
METADATA_PATH = INDEX_DIR / "chunks_metadata.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

BATCH_SIZE = 32


# --------------------------------------------------
# 2. LOAD THE CHUNKS
# --------------------------------------------------

def load_chunks():
    print("Loading agricultural chunks...")

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Chunk file not found: {CHUNKS_PATH}"
        )

    chunks = []

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            chunk = json.loads(line)

            if not chunk.get("text", "").strip():
                raise ValueError(
                    f"Empty chunk found at line {line_number}"
                )

            chunks.append(chunk)

    if not chunks:
        raise ValueError("No chunks found in the dataset.")

    print(f"Chunks loaded: {len(chunks)}")

    return chunks


# --------------------------------------------------
# 3. LOAD THE EMBEDDING MODEL
# --------------------------------------------------

def load_embedding_model():

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("\nLoading embedding model...")
    print(f"Model: {MODEL_NAME}")
    print(f"Device: {device}")

    model = SentenceTransformer(
        MODEL_NAME,
        device=device
    )

    embedding_dimension = model.get_sentence_embedding_dimension()

    print("Embedding model loaded successfully.")
    print(f"Embedding dimension: {embedding_dimension}")

    return model, embedding_dimension


# --------------------------------------------------
# 4. GENERATE EMBEDDINGS
# --------------------------------------------------

def generate_embeddings(model, chunks):

    print("\nGenerating embeddings...")

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    print("\nEmbedding generation completed.")
    print(f"Embedding matrix shape: {embeddings.shape}")

    return embeddings


# --------------------------------------------------
# 5. BUILD THE FAISS INDEX
# --------------------------------------------------

def build_faiss_index(embeddings):

    print("\nBuilding FAISS index...")

    embedding_dimension = embeddings.shape[1]

    # Inner product on normalized vectors gives
    # cosine similarity.
    index = faiss.IndexFlatIP(embedding_dimension)

    index.add(embeddings)

    print("FAISS index created successfully.")
    print(f"Vectors stored: {index.ntotal}")

    return index


# --------------------------------------------------
# 6. SAVE THE INDEX AND METADATA
# --------------------------------------------------

def save_index(index, chunks, embedding_dimension):

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    print("\nSaving FAISS index...")

    faiss.write_index(
        index,
        str(FAISS_PATH)
    )

    metadata = {
        "model_name": MODEL_NAME,
        "embedding_dimension": embedding_dimension,
        "similarity_metric": "cosine_similarity",
        "total_chunks": len(chunks),
        "chunks": chunks
    }

    print("Saving chunk metadata...")

    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\nFiles saved successfully:")
    print(f"FAISS index: {FAISS_PATH}")
    print(f"Metadata: {METADATA_PATH}")


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():

    start_time = time.time()

    print("=" * 60)
    print("AGRICULTURAL RAG - EMBEDDING AND FAISS INDEX BUILDER")
    print("=" * 60)

    chunks = load_chunks()

    model, embedding_dimension = load_embedding_model()

    embeddings = generate_embeddings(
        model,
        chunks
    )

    index = build_faiss_index(embeddings)

    if index.ntotal != len(chunks):
        raise RuntimeError(
            "FAISS vector count does not match chunk count."
        )

    save_index(
        index,
        chunks,
        embedding_dimension
    )

    elapsed_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("INDEX BUILDING COMPLETED")
    print("=" * 60)

    print(f"Total chunks: {len(chunks)}")
    print(f"Total vectors: {index.ntotal}")
    print(f"Embedding dimensions: {embedding_dimension}")
    print(f"Time taken: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
