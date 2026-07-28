from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    message: str


class ProductResponse(BaseModel):

    name: str
    price: str
    url: str
    image: str

    brand: Optional[str] = ""
    category: Optional[str] = ""


class ChatResponse(BaseModel):

    reply: str
    products: List[ProductResponse] = []