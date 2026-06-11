import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from sentence_transformers import SentenceTransformer
from database.db import SessionLocal
from database.models import KnowledgeChunk

CHROMA_PATH = Path(__file__).resolve().parent.parent.parent / "chroma_db"
TOP_K = 5

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
chroma_collection = chroma_client.get_or_create_collection("knowledge_base")


def search_knowledge_base(query: str, top_k: int = TOP_K):
    query_embedding = model.encode(query).tolist()
    results = chroma_collection.query(query_embeddings=[query_embedding], n_results=top_k)

    ids = results["ids"][0]
    distances = results["distances"][0]

    # Parse source_doc and chunk_index from ChromaDB IDs to fetch from PostgreSQL
    output = []
    db = SessionLocal()
    try:
        for chroma_id, distance in zip(ids, distances):
            # chroma_id format: "filename.md_idx"
            last_underscore = chroma_id.rfind("_")
            source_doc = chroma_id[:last_underscore]
            chunk_index = int(chroma_id[last_underscore + 1:])
            chunk = db.query(KnowledgeChunk).filter_by(
                source_doc=source_doc, chunk_index=chunk_index
            ).first()
            if chunk:
                output.append({
                    "id": chunk.id,
                    "source_doc": chunk.source_doc,
                    "chunk_text": chunk.chunk_text,
                    "distance": distance
                })
    finally:
        db.close()

    return output


if __name__ == "__main__":
    results = search_knowledge_base("Customer wants refund")
    for r in results:
        print(f"[{r['source_doc']}] distance={r['distance']:.4f}")
        print(r["chunk_text"][:300])
        print("-" * 60)
