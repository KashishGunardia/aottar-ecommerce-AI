from app.services.woo_service import WooCommerceService

wc = WooCommerceService()

products = wc.get_products()

keywords = [
    "dahua",
    "hikvision",
    "cp plus",
    "tp-link",
    "tplink",
    "ezviz"
]

for product in products:

    text = str(product).lower()

    for k in keywords:

        if k in text:
            print("=" * 80)
            print("FOUND:", k)
            print(product)
            break