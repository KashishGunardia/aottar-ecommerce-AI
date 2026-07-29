from fastapi import APIRouter, Request

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD"])
async def health(request: Request):
    return {
        "status": "healthy",
        "pipeline_ready": getattr(request.app.state, "pipeline_ready", False),
    }