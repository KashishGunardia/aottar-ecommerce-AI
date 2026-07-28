import re


class QueryClassifier:

    def __init__(self):

        self.greetings = {
            "hi", "hello", "hey", "hii", "good morning",
            "good afternoon", "good evening", "namaste",
            "namaskar", "hola"
        }

        self.order_keywords = [
            "order",
            "track",
            "tracking",
            "shipment",
            "delivery",
            "dispatch",
            "refund",
            "return",
            "replace",
            "cancel",
            "status"
        ]

        self.vendor_keywords = [
            "vendor",
            "seller",
            "sell",
            "partnership",
            "partner",
            "become vendor",
            "register vendor",
            "onboard"
        ]

        self.product_keywords = [
            # CCTV
            "camera", "cameras", "cctv", "dvr", "nvr",

            # Smart Home
            "switch", "switches",
            "smart switch", "touch switch",
            "lock", "locks", "smart lock",
            "doorbell",
            "light", "lights",
            "bulb",
            "curtain",
            "sensor",
            "plug",
            "socket",

            # Networking
            "router",
            "wifi",
            "access point",
            "lan",

            # Electrical
            "wire",
            "cable",
            "mcb",

            # Brands
            "auxo",
            "dashglasses",
            "aottor"
        ]

        self.use_case_keywords = [
            "home",
            "house",
            "office",
            "shop",
            "warehouse",
            "factory",
            "hotel",
            "hospital",
            "school",
            "building",
            "construction",
            "new house",
            "new office",
            "security",
            "automation"
        ]

        self.abuse_words = [
            "idiot",
            "stupid",
            "mad",
            "dumb",
            "fuck",
            "fucking",
            "shit",
            "bastard",
            "chutiya",
            "mc",
            "bc",
            "gandu",
            "harami"
        ]

    def classify(self, text):

        text = text.lower().strip()

        # Greeting
        if text in self.greetings:
            return "GREETING"

        # Abuse
        if any(word in text for word in self.abuse_words):
            return "ABUSE"

        # Order
        if any(word in text for word in self.order_keywords):
            return "ORDER"

        # Vendor
        if any(word in text for word in self.vendor_keywords):
            return "VENDOR"

        # PRODUCT gets highest priority
        if any(word in text for word in self.product_keywords):
            return "PRODUCT"

        # Budget usually means product search
        if re.search(r"under\s*\d+", text):
            return "PRODUCT"

        if re.search(r"below\s*\d+", text):
            return "PRODUCT"

        if re.search(r"\d+\s*rs", text):
            return "PRODUCT"

        if re.search(r"₹\s*\d+", text):
            return "PRODUCT"

        # Use Case
        if any(word in text for word in self.use_case_keywords):
            return "USE_CASE"

        # Hindi / Hinglish use cases
        if any(word in text for word in [
            "ghar",
            "office ke liye",
            "shop ke liye",
            "factory",
            "security chahiye",
            "camera lagana",
            "naya ghar",
            "bijli"
        ]):
            return "USE_CASE"

        return "GENERAL"