import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentence_transformers import SentenceTransformer

from database.db import SessionLocal
from database.models import KnowledgeChunk


# =====================================
# CONFIG
# =====================================

KB_FOLDER = Path(__file__).resolve().parent.parent.parent / "kb"

CHUNK_SIZE = 400

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

model = SentenceTransformer(EMBEDDING_MODEL)

db = SessionLocal()


# =====================================
# SIMPLE CHUNKER
# =====================================

def chunk_text(text, chunk_size=400):

    chunks = []

    for i in range(0, len(text), chunk_size):

        chunks.append(
            text[i:i + chunk_size]
        )

    return chunks


# =====================================
# PROCESS FILE
# =====================================

def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:

        content = f.read()

    chunks = chunk_text(content)

    for idx, chunk in enumerate(chunks):

        embedding = model.encode(
            chunk
        ).tolist()

        kb_chunk = KnowledgeChunk(
            source_doc=filepath.name,
            chunk_index=idx,
            chunk_text=chunk,
            embedding=embedding
        )

        db.add(kb_chunk)

    db.commit()

    print(
        f"Stored {len(chunks)} chunks "
        f"from {filepath.name}"
    )


# =====================================
# MAIN
# =====================================

def build_knowledge_base():

    files = list(
        KB_FOLDER.glob("*.md")
    )

    print(
        f"Found {len(files)} KB documents"
    )

    for file in files:

        process_file(file)

    print()

    print(
        "Knowledge Base Created Successfully"
    )


if __name__ == "__main__":

    build_knowledge_base()

    db.close()