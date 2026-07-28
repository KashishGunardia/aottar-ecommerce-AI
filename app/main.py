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

@app.get("/", tags=["Home"])
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

@app.on_event("startup")
async def start_product_sync():
    # Build the ChatService pipeline (embedding model, FAISS index, BM25,
    # WooCommerce fetch) in a background thread instead of blocking here.
    # uvicorn has already bound $PORT by the time this startup event runs,
    # so Render's port scan succeeds immediately; the pipeline finishes
    # warming up a few seconds/minutes later without holding up the deploy.
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, get_chat_service)

    # get_chat_service() is a singleton getter, so this reloads the exact
    # index the /chat/ route searches against — no restart needed after a
    # WooCommerce product change.
    init_product_sync(lambda: get_chat_service().pipeline.hybrid)


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