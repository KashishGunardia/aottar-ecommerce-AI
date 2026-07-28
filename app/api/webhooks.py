from fastapi import APIRouter, BackgroundTasks, Request

router = APIRouter()

@router.post("/woocommerce/product")
async def product_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):

    payload = await request.json()

    background_tasks.add_task(
        process_product,
        payload
    )

    return {
        "success": True
    }