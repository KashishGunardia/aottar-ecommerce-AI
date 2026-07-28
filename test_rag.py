from app.rag.retriever import get_retriever

retriever = get_retriever()

docs = retriever.invoke("camera")

for d in docs:
    print(d.metadata)