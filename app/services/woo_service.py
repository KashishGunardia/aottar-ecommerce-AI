import os
import requests
from dotenv import load_dotenv

load_dotenv()


class WooCommerceService:

    def __init__(self):

        self.base_url = os.getenv("WC_URL")
        self.consumer_key = os.getenv("WC_CONSUMER_KEY")
        self.consumer_secret = os.getenv("WC_CONSUMER_SECRET")

    def get_products(self):

        all_products = []
        page = 1

        while True:

            response = requests.get(

                f"{self.base_url}/wp-json/wc/v3/products",

                params={
                    "consumer_key": self.consumer_key,
                    "consumer_secret": self.consumer_secret,
                    "per_page": 100,
                    "page": page,
                    "status": "publish"
                },

                # Without a timeout, requests waits forever if the
                # WooCommerce site is slow/unreachable. That previously hung
                # app startup indefinitely (ChatService/ShoppingPipeline are
                # built at import time), which meant uvicorn never got to
                # bind the port and Render's deploy timed out.
                timeout=15,

            )

            response.raise_for_status()

            products = response.json()

            if not products:
                break

            print(f"Fetched Page {page}: {len(products)} products")

            all_products.extend(products)

            page += 1

        print(f"\nTotal Products Downloaded: {len(all_products)}")

        return all_products