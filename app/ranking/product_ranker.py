class ProductRanker:

    def score(self, product, entities):

        score = 0

        # -------------------------
        # Brand
        # -------------------------

        if entities.get("brand"):

            if entities["brand"].lower() in product["brand"].lower():

                score += 40

        # -------------------------
        # Category
        # -------------------------

        if entities.get("category"):

            if entities["category"].lower() in product["category"].lower():

                score += 30

        # -------------------------
        # Budget
        # -------------------------

        if entities.get("budget"):

            try:

                if float(product["price"]) <= entities["budget"]:

                    score += 20

            except:

                pass

        # -------------------------
        # Smart Feature
        # -------------------------

        if "smart" in entities.get("feature", []):

            if "smart" in product["name"].lower():

                score += 5

        # -------------------------
        # WiFi
        # -------------------------

        if "wifi" in entities.get("feature", []):

            if "wifi" in product["name"].lower():

                score += 5

        return score

    def rank(self, products, entities):

        ranked = sorted(

            products,

            key=lambda p: self.score(p, entities),

            reverse=True

        )

        return ranked