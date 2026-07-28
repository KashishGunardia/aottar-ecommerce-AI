"""
Vendor -> WooCommerce -> [this service, on a schedule] -> local cache
                                                        -> FAISS index
                                                        -> live chatbot

Whenever a vendor adds/edits a product in WooCommerce, this service (run on
an interval by app/core/scheduler.py) fetches the full current catalog,
writes it to a local JSON cache (products_cache.json, used by BM25/product
listing), rebuilds the FAISS vector index from it, and hot-swaps both into
the already-running HybridSearch instance so the chatbot picks up the
change without a server restart.
"""

import json
import os
import threading
from datetime import datetime, timezone

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.logger import logger
from app.rag.embeddings import get_embedding_model
from app.services.woo_service import WooCommerceService

CACHE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "products_cache.json")
)

INDEX_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "rag", "product_index")
)


def _clean_product(p):

    category = ""

    if p.get("categories"):
        category = ", ".join(c["name"] for c in p["categories"])

    brand = ""

    if p.get("brands"):
        brand = ", ".join(b["name"] for b in p["brands"])

    image = ""

    if p.get("images"):
        image = p["images"][0]["src"]

    return {
        "id": p.get("id"),
        "name": p.get("name"),
        "brand": brand,
        "category": category,
        "price": p.get("price"),
        "url": p.get("permalink"),
        "image": image,
        "short_description": p.get("short_description", ""),
        "description": p.get("description", ""),
    }


def _build_documents(products):

    documents = []

    for p in products:

        text = f"""
Product Name:
{p['name']}

Brand:
{p['brand']}

Category:
{p['category']}

Price:
₹{p['price']}

Short Description:
{p['short_description']}

Description:
{p['description']}
"""

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "id": p["id"],
                    "name": p["name"],
                    "price": p["price"],
                    "url": p["url"],
                    "image": p["image"],
                    "category": p["category"],
                    "brand": p["brand"],
                },
            )
        )

    return documents


class ProductSyncService:
    """
    Call sync_once() on an interval (see app/core/scheduler.py) or from an
    admin endpoint to refresh products from WooCommerce.
    """

    def __init__(self, get_hybrid_search):
        """
        get_hybrid_search: zero-arg callable returning the live HybridSearch
        instance used by the running chatbot, so we can hot-reload it after
        every sync. Passed as a callable (not the instance itself) so the
        scheduler doesn't need to care about import order/circular imports.
        """
        self._get_hybrid_search = get_hybrid_search
        self._lock = threading.Lock()

        self.last_synced_at = None
        self.last_product_count = 0
        self.last_error = None

    def sync_once(self):

        if not self._lock.acquire(blocking=False):
            logger.info("⏭️  Product sync already running, skipping this tick")
            return

        try:
            logger.info("🔄 Product sync started (WooCommerce → cache → FAISS)")

            wc = WooCommerceService()

            raw_products = wc.get_products()

            products = [_clean_product(p) for p in raw_products]

            # ------------------------------
            # Update local cache (source of truth for BM25 / product listing)
            # ------------------------------

            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            # ------------------------------
            # Rebuild FAISS vector index
            # ------------------------------

            documents = _build_documents(products)

            embeddings = get_embedding_model()

            db = FAISS.from_documents(documents, embeddings)

            db.save_local(INDEX_PATH)

            # ------------------------------
            # Hot-reload the live chatbot's search index
            # ------------------------------

            hybrid = self._get_hybrid_search()

            if hybrid is not None:
                hybrid.reload(faiss_db=db, products=products)

            self.last_synced_at = datetime.now(timezone.utc)
            self.last_product_count = len(products)
            self.last_error = None

            logger.info(
                f"✅ Product sync complete — {len(products)} products indexed"
            )

        except Exception as e:
            self.last_error = str(e)
            logger.error(f"❌ Product sync failed: {e}")

        finally:
            self._lock.release()

    def status(self):
        return {
            "last_synced_at": (
                self.last_synced_at.isoformat() if self.last_synced_at else None
            ),
            "last_product_count": self.last_product_count,
            "last_error": self.last_error,
        }
