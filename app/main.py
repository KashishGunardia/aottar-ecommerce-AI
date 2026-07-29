import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import logger
from app.core.scheduler import init_product_sync, shutdown_scheduler

from app.api.health import router as health_router
from app.api.chat import router as chat_router, get_chat_service
from app.api.products import router as products_router
from app.api.vendors import router as vendors_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Aottar AI Chatbot",
)

# ==========================================
# CORS Configuration
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aottar.com",
        "https://www.aottar.com",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Root Endpoint
# ==========================================

@app.api_route("/", methods=["GET", "HEAD"], tags=["Home"])
async def root():
    return {
        "message": "🚀 Welcome to Aottar AI Backend",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }

# ==========================================
# Register Routers
# ==========================================

app.include_router(health_router, tags=["Health"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(vendors_router, prefix="/vendors", tags=["Vendors"])

# ==========================================
# Vendor -> WooCommerce -> Cache -> FAISS -> Chatbot sync
# ==========================================

# Tracks whether the ChatService pipeline (embedding model, FAISS index,
# BM25, WooCommerce fetch) has finished warming up. Exposed on /health so
# you can tell whether the app is up but still loading vs fully ready.
app.state.pipeline_ready = False


async def _warm_up_pipeline():
    """
    Builds the ChatService pipeline in the background.

    IMPORTANT: this must NOT be awaited directly inside the `startup` event.
    uvicorn does not start accepting connections until the startup event
    returns, so awaiting slow work here (loading torch/sentence-transformers
    models, hitting WooCommerce) reproduces the exact "no open ports
    detected" timeout this function exists to avoid. Firing it as a
    background task lets `startup` return immediately.
    """
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, get_chat_service)
        app.state.pipeline_ready = True
        logger.info("✅ Chat pipeline warmed up and ready")
    except Exception:
        logger.exception(
            "❌ Chat pipeline failed to warm up - will retry via the "
            "scheduled product sync below"
        )
    finally:
        # Start the sync scheduler regardless of whether the pipeline
        # above succeeded. If it failed (e.g. WooCommerce was briefly
        # unreachable), the next scheduled sync_once() still rebuilds a
        # real FAISS/BM25 index and hot-reloads it via get_chat_service()
        # here, self-healing without needing a manual restart.
        init_product_sync(lambda: get_chat_service().pipeline.hybrid)


@app.on_event("startup")
async def start_product_sync():
    asyncio.create_task(_warm_up_pipeline())


@app.on_event("shutdown")
def stop_product_sync():
    shutdown_scheduler()


@app.get("/admin/sync-status", tags=["Admin"])
async def sync_status():
    from app.core import scheduler as scheduler_module

    if scheduler_module.product_sync_service is None:
        return {"status": "not started yet"}

    return scheduler_module.product_sync_service.status()


@app.post("/admin/sync-now", tags=["Admin"])
async def sync_now():
    from app.core import scheduler as scheduler_module

    if scheduler_module.product_sync_service is None:
        return {"success": False, "detail": "Scheduler not started yet"}

    scheduler_module.product_sync_service.sync_once()

    return {"success": True, **scheduler_module.product_sync_service.status()}


logger.info("🚀 Aottar AI Backend Started Successfully")