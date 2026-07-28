import os
import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.get(
    f"{os.getenv('WC_URL')}/wp-json/wc/v3/products",
    params={
        "consumer_key": os.getenv("WC_CONSUMER_KEY"),
        "consumer_secret": os.getenv("WC_CONSUMER_SECRET"),
        "search": "dahua",
        "per_page": 100
    }
)

print(response.status_code)
print(response.json())