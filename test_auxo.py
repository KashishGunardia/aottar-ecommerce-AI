from app.services.woo_service import WooCommerceService

wc = WooCommerceService()

products = wc.get_products()

for p in products:

    brand = ""

    if p.get("brands"):
        brand = p["brands"][0]["name"]

    if brand.upper() == "AUXO":

        print(
            p["name"],
            "₹" + p["price"],
            p["categories"][0]["name"]
        )