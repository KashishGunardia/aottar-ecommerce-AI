import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.services.woo_service import WooCommerceService
from app.rag.embeddings import get_embedding_model


def create_vector_db():

    print("Fetching products from WooCommerce...")

    wc = WooCommerceService()

    products = wc.get_products()

    print(f"\nTotal Products Found: {len(products)}\n")


    for p in products[:10]:
        print("-", p["name"])


    documents = []


    for product in products:


        # -------------------------
        # Category
        # -------------------------

        category = ""

        if product.get("categories"):
            category = ", ".join(
                c["name"]
                for c in product["categories"]
            )


        # -------------------------
        # Brand
        # -------------------------

        brand = ""

        if product.get("brands"):
            brand = ", ".join(
                b["name"]
                for b in product["brands"]
            )


        # -------------------------
        # Image
        # -------------------------

        image = ""

        if product.get("images"):
            image = product["images"][0]["src"]


        # -------------------------
        # Product Text
        # -------------------------

        text = f"""
Product Name:
{product.get("name")}

Brand:
{brand}

Category:
{category}

Price:
₹{product.get("price")}

Short Description:
{product.get("short_description","")}

Description:
{product.get("description","")}
"""


        documents.append(

            Document(

                page_content=text,

                metadata={

                    "id": product.get("id"),

                    "name": product.get("name"),

                    "price": product.get("price"),

                    "url": product.get("permalink"),

                    "image": image,

                    "category": category,

                    "brand": brand

                }

            )

        )


    print(
        f"Creating embeddings for {len(documents)} products..."
    )


    embeddings = get_embedding_model()


    db = FAISS.from_documents(
        documents,
        embeddings
    )


    save_path = os.path.join(
        os.path.dirname(__file__),
        "product_index"
    )


    db.save_local(save_path)


    print(
        "✅ WooCommerce Vector DB Created Successfully"
    )



if __name__ == "__main__":
    create_vector_db()