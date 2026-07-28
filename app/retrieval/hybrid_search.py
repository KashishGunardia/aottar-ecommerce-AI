from app.rag.retriever import get_retriever
from app.retrieval.bm25_search import BM25Search
from app.retrieval.product_loader import load_products


class HybridSearch:

    def __init__(self):

        self.faiss = get_retriever()
        self.bm25 = BM25Search(load_products())

    def reload(self, faiss_db=None, products=None):
        """
        Hot-swaps the in-memory FAISS retriever and BM25 corpus after a
        WooCommerce product sync, so newly added/edited vendor products
        show up in chat without restarting the backend.

        - faiss_db: an already-built FAISS vectorstore (avoids re-loading
          from disk when the sync job just built it in-process). If not
          given, reloads from the saved index on disk instead.
        - products: the freshly-synced clean product list for BM25. If not
          given, reloads from the products cache file on disk.
        """

        if faiss_db is not None:
            self.faiss = faiss_db.as_retriever(search_kwargs={"k": 25})
        else:
            self.faiss = get_retriever()

        self.bm25 = BM25Search(products if products is not None else load_products())

    def search(self, query):

        faiss_docs = self.faiss.invoke(query)

        bm25_docs = self.bm25.search(query)

        merged = []
        seen = set()

        for p in bm25_docs:

            if p["id"] not in seen:
                merged.append(p)
                seen.add(p["id"])

        for d in faiss_docs:

            pid = d.metadata["id"]

            if pid not in seen:

                merged.append({
                    "id": pid,
                    "name": d.metadata["name"],
                    "brand": d.metadata["brand"],
                    "category": d.metadata["category"],
                    "price": d.metadata["price"],
                    "url": d.metadata["url"],
                    "image": d.metadata["image"],
                })

                seen.add(pid)

        return merged