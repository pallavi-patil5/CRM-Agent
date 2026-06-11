import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import APIRouter, Query
from rag.retriever import search_knowledge_base


router = APIRouter(prefix="/rag", tags=["RAG"])


@router.get("/search")
def rag_search(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of chunks to return")
):
    """Debug endpoint: query knowledge base and return chunks with similarity scores."""
    results = search_knowledge_base(q, top_k=top_k)
    return {
        "query": q,
        "results": [
            {
                "rank": i + 1,
                "source_doc": r["source_doc"],
                "chunk_text": r["chunk_text"],
                "similarity_distance": round(r["distance"], 4)
            }
            for i, r in enumerate(results)
        ]
    }
