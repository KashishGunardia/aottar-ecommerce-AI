from app.services.woo_service import WooCommerceService
import json

wc = WooCommerceService()

products = wc.get_products()

print(f"Total Products: {len(products)}")

print(json.dumps(products[0], indent=4))