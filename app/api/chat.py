import hashlib

from fastapi import APIRouter, HTTPException, Request

from app.database.schemas import (
    ChatRequest,
    ProductResponse,
)

from app.services.chat_service import ChatService

router = APIRouter()

# ChatService() builds the whole pipeline (embedding model, FAISS index,
# BM25 corpus, WooCommerce fetch) - this used to run at import time, which
# blocks uvicorn from ever binding to $PORT until it finishes. On Render
# that meant the deploy timed out before the server ever started listening.
# It's now built lazily on first use, and eagerly "warmed up" in the
# background from main.py's startup event (after the port is already open).
_chat_service = None


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


def _derive_session_key(http_request: Request) -> str:
    """
    Derives a per-visitor session key from IP + User-Agent since the
    WordPress frontend isn't sending an explicit session/conversation id.

    NOTE: this is a best-effort fallback, not a true session id — visitors
    sharing an IP (office wifi, mobile carrier NAT, VPN) will be bucketed
    together. If the frontend is ever able to send a real session_id
    (e.g. a localStorage-generated UUID), prefer that instead.
    """

    client_ip = http_request.client.host if http_request.client else "unknown"
    user_agent = http_request.headers.get("user-agent", "unknown")

    raw_key = f"{client_ip}:{user_agent}"

    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]


@router.post("/")
async def chat(request: ChatRequest, http_request: Request):
    try:
        session_key = _derive_session_key(http_request)

        result = get_chat_service().chat(request.message, session_key=session_key)

        response = {
            "success": True,
            "type": result.get("type", "text"),
            "message": result.get("message", ""),
            "typing": result.get("typing", False),
            "quick_replies": result.get("quick_replies", []),
            "actions": result.get("actions", []),
            "metadata": result.get("metadata", {}),
        }

        # Add product cards
        if result.get("products"):
            response["products"] = [
                ProductResponse(**product)
                for product in result["products"]
            ]

        # Vendor information
        if result.get("vendor"):
            response["vendor"] = result["vendor"]

        # FAQ cards
        if result.get("faqs"):
            response["faqs"] = result["faqs"]

        # Category cards
        if result.get("categories"):
            response["categories"] = result["categories"]

        # Suggested questions
        if result.get("suggestions"):
            response["suggestions"] = result["suggestions"]

        # Redirect support
        if result.get("redirect"):
            response["redirect"] = result["redirect"]

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )