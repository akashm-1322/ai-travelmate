from app.rag.documents import (
    load_documents,
    chunk_text
)

from app.rag.embeddings import (
    create_embedding
)

from app.rag.vector_store import (
    add_document
)


def ingest():

    documents = load_documents()

    total_chunks = 0

    for document in documents:

        source = document["source"]

        chunks = chunk_text(
            document["text"]
        )

        for index, chunk in enumerate(chunks):

            embedding = create_embedding(
                chunk
            )

            document_id = (
                f"{source}-{index}"
            )

            add_document(
                document_id=document_id,
                text=chunk,
                embedding=embedding,
                metadata={
                    "source": source
                }
            )

            total_chunks += 1

            print(
                f"Indexed: {document_id}"
            )

    print(
        f"\nIngestion complete."
        f"\nDocuments: {len(documents)}"
        f"\nChunks: {total_chunks}"
    )


if __name__ == "__main__":
    ingest()