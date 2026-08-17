from pathlib import Path


DATA_DIR = Path("data/travel")


def load_documents():

    documents = []

    for file_path in DATA_DIR.glob("*.md"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100
):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks