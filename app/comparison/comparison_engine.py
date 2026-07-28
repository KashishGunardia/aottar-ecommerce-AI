from typing import List


class ComparisonEngine:

    def compare(self, products: List[dict]):

        if len(products) < 2:
            return None

        comparison = []

        for product in products[:2]:

            comparison.append({
                "Name": product.get("name", "N/A"),
                "Brand": product.get("brand", "N/A"),
                "Category": product.get("category", "N/A"),
                "Price": f"₹{product.get('price', 'N/A')}"
            })

        return comparison