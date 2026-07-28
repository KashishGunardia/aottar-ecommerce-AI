from app.services.woo_service import WooCommerceService


class InventoryEngine:

    def __init__(self):

        self.wc = WooCommerceService()

    def refresh_products(self, products):

        refreshed = []

        for product in products:

            try:

                latest = self.wc.get_product(
                    product["id"]
                )

                refreshed.append({

                    "id": latest["id"],

                    "name": latest["name"],

                    "price": latest["price"],

                    "url": latest["permalink"],

                    "image": latest["images"][0]["src"]
                    if latest["images"] else "",

                    "brand": product.get("brand"),

                    "category": product.get("category"),

                    "stock_status": latest.get(
                        "stock_status",
                        "unknown"
                    ),

                    "stock_quantity": latest.get(
                        "stock_quantity"
                    )

                })

            except:

                refreshed.append(product)

        return refreshed