
import json
import numpy as np

from pathlib import Path


CHUNKS_PATH = Path("data/processed/chunks.jsonl")
EMBEDDINGS_PATH = Path("data/processed/embeddings.npy")
CHUNK_IDS_PATH = Path("data/processed/embedding_chunk_ids.npy")


def validate_embeddings():

    embeddings = np.load(EMBEDDINGS_PATH)
    chunk_ids = np.load(CHUNK_IDS_PATH)

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    print("EMBEDDING VALIDATION")
    print("=" * 50)

    print(f"Embedding shape: {embeddings.shape}")
    print(f"Chunk ID shape: {chunk_ids.shape}")
    print(f"Number of source chunks: {len(chunks)}")

    # Check dimensions
    assert embeddings.ndim == 2
    assert embeddings.shape[1] == 384

    # Check row counts
    assert embeddings.shape[0] == len(chunks)
    assert len(chunk_ids) == len(chunks)

    # Check chunk ID mapping
    expected_ids = np.array(
        [chunk["chunk_id"] for chunk in chunks],
        dtype=np.int32
    )

    assert np.array_equal(chunk_ids, expected_ids)

    # Check numerical validity
    assert np.isfinite(embeddings).all()

    # Check vector normalization
    norms = np.linalg.norm(embeddings, axis=1)

    assert np.allclose(norms, 1.0, atol=1e-5)

    print("\nAll checks passed!")
    print(f"Total vectors: {len(embeddings)}")
    print(f"Dimensions per vector: {embeddings.shape[1]}")
    print(f"Minimum vector norm: {norms.min():.6f}")
    print(f"Maximum vector norm: {norms.max():.6f}")
    print(f"Data type: {embeddings.dtype}")


if __name__ == "__main__":
    validate_embeddings()
