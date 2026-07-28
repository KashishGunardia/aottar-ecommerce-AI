class ProductReranker:

    def score(self, product, entities):

        score = 0

        # --------------------------
        # Brand Match
        # --------------------------
        if entities.get("brand"):

            if product.get("brand", "").lower() == entities["brand"].lower():
                score += 50

        # --------------------------
        # Category Match
        # --------------------------
        if entities.get("category"):

            category = product.get("category", "").lower()

            if entities["category"].lower() in category:
                score += 40

        # --------------------------
        # Budget Match
        # --------------------------
        if entities.get("budget"):

            try:
                price = int(float(product["price"]))

                if price <= entities["budget"]:
                    score += 30

            except:
                pass

        # --------------------------
        # Feature Match
        # --------------------------
        if entities.get("feature"):

            text = (
                product.get("name", "") +
                " " +
                product.get("category", "")
            ).lower()

            for feature in entities["feature"]:

                if feature.lower() in text:
                    score += 10

        # --------------------------
        # Quantity
        # --------------------------
        if entities.get("quantity"):

            score += 5

        # --------------------------
        # Use Case
        # --------------------------
        if entities.get("use_case"):

            score += 5

        return score

    def rerank(self, products, entities):

        ranked = sorted(
            products,
            key=lambda p: self.score(p, entities),
            reverse=True
        )

        return ranked