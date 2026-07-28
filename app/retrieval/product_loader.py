import json
import os

from app.services.woo_service import WooCommerceService

CACHE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "products_cache.json")
)


def _clean_product(p):

    category = ""

    if p.get("categories"):
        category = ", ".join(c["name"] for c in p["categories"])

    brand = ""

    if p.get("brands"):
        brand = p["brands"][0]["name"]

    return {
        "id": p["id"],
        "name": p["name"],
        "category": category,
        "brand": brand,
        "price": p["price"],
        "url": p["permalink"],
        "image": p["images"][0]["src"] if p["images"] else "",
    }


def load_products():
    """
    Loads the product catalog for BM25/search.

    Prefers the local cache (app/data/products_cache.json), which the
    scheduled WooCommerce sync keeps fresh every 15-30 minutes. Falls back
    to a live WooCommerce fetch only if no cache exists yet (e.g. first
    boot before the initial sync has completed).
    """

    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    wc = WooCommerceService()

    products = wc.get_products()

    return [_clean_product(p) for p in products]