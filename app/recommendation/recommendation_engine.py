from typing import List


class RecommendationEngine:

    def recommend(self, products: List[dict], entities: dict):

        if not products:
            return []

        budget = entities.get("budget")

        brand = entities.get("brand")

        category = entities.get("category")

        scored = []

        for product in products:

            score = 0

            # -------------------------
            # Category Match
            # -------------------------

            if category:

                if category.lower() in product.get(
                    "category",
                    ""
                ).lower():

                    score += 50

            # -------------------------
            # Brand Match
            # -------------------------

            if brand:

                if brand.lower() in product.get(
                    "brand",
                    ""
                ).lower():

                    score += 30

            # -------------------------
            # Budget Match
            # -------------------------

            if budget:

                try:

                    price = float(product["price"])

                    if price <= budget:

                        score += 20

                except:

                    pass

            product["score"] = score

            scored.append(product)

        scored.sort(

            key=lambda x: x["score"],

            reverse=True

        )

        return scored[:5]