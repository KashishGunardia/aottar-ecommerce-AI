import os

from langchain_community.vectorstores import FAISS

from app.rag.embeddings import get_embedding_model


def get_retriever():

    embeddings = get_embedding_model()

    db = FAISS.load_local(
        os.path.join(
            os.path.dirname(__file__),
            "product_index",
        ),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    retriever = db.as_retriever(
        search_kwargs={"k": 25}
    )

    return retriever