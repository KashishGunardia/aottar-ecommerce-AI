"""
Runs the WooCommerce -> cache -> FAISS product sync on a schedule, in-process,
for as long as the FastAPI app is running (no external cron needed).
"""

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.logger import logger
from app.services.product_sync_service import ProductSyncService

SYNC_INTERVAL_MINUTES = 20  # anywhere in the 15-30 min window works

_scheduler = BackgroundScheduler()
product_sync_service: ProductSyncService | None = None


def init_product_sync(get_hybrid_search):
    """
    Creates the ProductSyncService and starts the recurring sync job.
    get_hybrid_search: zero-arg callable returning the live HybridSearch
    instance to hot-reload after each sync (see app/api/chat.py).
    """

    global product_sync_service

    product_sync_service = ProductSyncService(get_hybrid_search)

    # Run once immediately on startup (in the background, so it doesn't
    # block the app from accepting requests), then on a fixed interval.
    _scheduler.add_job(
        product_sync_service.sync_once,
        id="woocommerce_product_sync_initial",
        replace_existing=True,
    )

    _scheduler.add_job(
        product_sync_service.sync_once,
        "interval",
        minutes=SYNC_INTERVAL_MINUTES,
        id="woocommerce_product_sync",
        replace_existing=True,
    )

    _scheduler.start()

    logger.info(
        f"🕒 Product sync scheduler started (every {SYNC_INTERVAL_MINUTES} min)"
    )


def shutdown_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
