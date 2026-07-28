from fastapi import APIRouter
from app.services.product_service import ProductService

router = APIRouter()

product_service = ProductService()


@router.get("/")
async def get_products():
    return product_service.get_all_products()


@router.get("/search")
async def search_products(query: str):
    return product_service.search_products(query)