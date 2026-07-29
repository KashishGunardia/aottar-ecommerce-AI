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

                # HTTP Basic Auth instead of ?consumer_key=...&consumer_secret=...
                # in the URL. WooCommerce supports both over HTTPS, but some
                # hosting firewalls/security plugins (Wordfence, Sucuri,
                # Cloudflare) specifically flag credentials showing up in a
                # query string as suspicious and block the request with a 403.
                # Basic Auth avoids that, and also keeps the keys out of any
                # server access logs.
                auth=(self.consumer_key, self.consumer_secret),

                params={
                    "per_page": 100,
                    "page": page,
                    "status": "publish"
                },

                # Some of the same firewalls/security plugins also block the
                # default "python-requests/x.x" User-Agent outright as an
                # obvious bot signature - a normal browser-style UA is far
                # less likely to get challenged/blocked.
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept": "application/json",
                },

                # Without a timeout, requests waits forever if the
                # WooCommerce site is slow/unreachable. That previously hung
                # app startup indefinitely (ChatService/ShoppingPipeline are
                # built at import time), which meant uvicorn never got to
                # bind the port and Render's deploy timed out.
                timeout=15,

            )

            if not response.ok:
                # Surface the response body (WAFs/security plugins usually
                # explain the block here) instead of just the generic
                # "403 Forbidden" from raise_for_status(), so the real cause
                # shows up in /admin/sync-status and the logs.
                raise requests.HTTPError(
                    f"{response.status_code} error fetching WooCommerce "
                    f"products (page {page}): {response.text[:500]}"
                )

            products = response.json()

            if not products:
                break

            print(f"Fetched Page {page}: {len(products)} products")

            all_products.extend(products)

            page += 1

        print(f"\nTotal Products Downloaded: {len(all_products)}")

        return all_products