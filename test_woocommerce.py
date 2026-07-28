import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = f"{os.getenv('WC_URL')}/wp-json/wc/v3/products"

response = requests.get(
    url,
    auth=(
        os.getenv("WC_CONSUMER_KEY"),
        os.getenv("WC_CONSUMER_SECRET")
    )
)

print("Status Code:", response.status_code)

if response.status_code == 200:

    products = response.json()

    print(f"\nFound {len(products)} products\n")

    for product in products[:5]:

        print("=" * 50)
        print("Name :", product["name"])
        print("Price:", product["price"])
        print("URL  :", product["permalink"])

        if product["images"]:
            print("Image:", product["images"][0]["src"])

        print("=" * 50)

else:
    print(response.text)