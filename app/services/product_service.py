class ProductService:

    def __init__(self):
        self.products = [
            {
                "id": 1,
                "name": "Dahua 2MP Bullet Camera",
                "brand": "Dahua",
                "category": "CCTV Camera",
                "price": 2499
            },
            {
                "id": 2,
                "name": "CP Plus DVR 8 Channel",
                "brand": "CP Plus",
                "category": "DVR",
                "price": 5999
            },
            {
                "id": 3,
                "name": "Hikvision Dome Camera",
                "brand": "Hikvision",
                "category": "CCTV Camera",
                "price": 3199
            }
        ]

    def get_all_products(self):
        return self.products

    def search_products(self, query: str):
        query = query.lower()

        return [
            product for product in self.products
            if (
                query in product["name"].lower()
                or query in product["brand"].lower()
                or query in product["category"].lower()
            )
        ]