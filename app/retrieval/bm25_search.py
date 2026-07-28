from rank_bm25 import BM25Okapi


class BM25Search:

    def __init__(self, products):

        self.products = products

        corpus = []

        for p in products:

            text = (
                p["name"] + " " +
                p["category"] + " " +
                p["brand"]
            )

            corpus.append(text.lower().split())

        self.bm25 = BM25Okapi(corpus)

    def search(self, query, top_k=20):

        tokens = query.lower().split()

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.products, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [x[0] for x in ranked[:top_k]]