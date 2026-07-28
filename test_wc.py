from app.services.woo_service import WooCommerceService

wc = WooCommerceService()

products = wc.get_products()

count = 0

for p in products:

    name = p.get("name", "")

    if "dahua" in name.lower():
        print(name)
        count += 1

print("\nTotal Dahua Products:", count)