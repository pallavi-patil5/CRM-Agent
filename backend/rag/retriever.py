import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from sentence_transformers import SentenceTransformer
from database.db import SessionLocal
from database.models import KnowledgeChunk


TOP_K = 5
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(query):
    return model.encode(query).tolist()


def cosine_distance(a, b):
    a, b = np.array(a), np.array(b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 1.0
    return 1.0 - float(np.dot(a, b) / norm)


def search_knowledge_base(query: str, top_k: int = TOP_K):
    query_embedding = generate_embedding(query)

    db = SessionLocal()
    try:
        chunks = db.query(KnowledgeChunk).all()
    finally:
        db.close()

    if not chunks:
        return []

    scored = []
    for chunk in chunks:
        if chunk.embedding is None:
            continue
        emb = chunk.embedding if isinstance(chunk.embedding, list) else list(chunk.embedding)
        distance = cosine_distance(query_embedding, emb)
        scored.append({
            "id": chunk.id,
            "source_doc": chunk.source_doc,
            "chunk_text": chunk.chunk_text,
            "distance": distance
        })

    scored.sort(key=lambda x: x["distance"])
    return scored[:top_k]


if __name__ == "__main__":
    results = search_knowledge_base("Customer wants refund")
    for r in results:
        print(f"[{r['source_doc']}] distance={r['distance']:.4f}")
        print(r["chunk_text"][:300])
        print("-" * 60)
