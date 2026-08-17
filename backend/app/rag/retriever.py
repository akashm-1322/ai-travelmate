from app.rag.embeddings import (
    create_embedding
)

from app.rag.vector_store import (
    search
)


def retrieve(
    query: str,
    top_k: int = 5
):

    query_embedding = create_embedding(
        query
    )

    results = search(
        query_embedding,
        top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    retrieved = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        retrieved.append({
            "text": document,
            "metadata": metadata
        })

    return retrieved