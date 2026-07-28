from app.services.woo_service import WooCommerceService

wc = WooCommerceService()

products = wc.get_products()

brands = set()

for p in products:
    for b in p.get("brands", []):
        brands.add(b["name"])

print("\nBrands Found:\n")
print(sorted(brands))