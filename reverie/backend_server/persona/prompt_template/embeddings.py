"""
Local embeddings using sentence-transformers.
Replaces OpenAI embeddings with all-MiniLM-L6-v2 model for cost-free operation.

Model: all-MiniLM-L6-v2
- Produces 384-dimensional embeddings
- Fast and efficient for semantic similarity
- Runs locally on CPU/GPU
"""
import numpy as np
from typing import List, Optional
import threading

# Lazy-load model to avoid slow startup (thread-safe)
_model = None
_model_lock = threading.Lock()


def get_model():
    """Get or initialize the embedding model (lazy loading, thread-safe)."""
    global _model
    if _model is None:
        with _model_lock:
            # Double-check after acquiring lock
            if _model is None:
                print("[Embeddings] Loading all-MiniLM-L6-v2 model...")
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[Embeddings] Model loaded successfully.")
    return _model


def get_embedding(text: str) -> List[float]:
    """
    Get embedding for text using local sentence-transformers model.

    Args:
        text: Text to embed

    Returns:
        384-dimensional embedding vector as list of floats
    """
    text = text.replace("\n", " ").strip()
    if not text:
        text = "this is blank"

    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for multiple texts efficiently (batched processing).

    Args:
        texts: List of texts to embed

    Returns:
        List of 384-dimensional embedding vectors
    """
    cleaned = [t.replace("\n", " ").strip() or "this is blank" for t in texts]
    model = get_model()
    embeddings = model.encode(cleaned, convert_to_numpy=True, show_progress_bar=False)
    return [e.tolist() for e in embeddings]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score (0-1)
    """
    if not vec1 or not vec2:
        return 0.0

    a = np.array(vec1)
    b = np.array(vec2)

    # Handle dimension mismatch by truncating to smaller
    min_len = min(len(a), len(b))
    a = a[:min_len]
    b = b[:min_len]

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


# Dimension of embeddings from this model
EMBEDDING_DIM = 384
