import re


class EntityExtractor:

    def extract(self, message):

        text = message.lower()

        entity = {

            "brand": None,

            "category": None,

            "budget": None,

            "use_case": None

        }

        # -------------------------
        # Budget
        # -------------------------

        budget = re.search(r"(\d{3,7})", text)

        if budget:

            entity["budget"] = int(budget.group(1))

        # -------------------------
        # Brand
        # -------------------------

        brands = [

            "dahua",
            "hikvision",
            "cp plus",
            "cpplus",
            "tp-link",
            "tplink",
            "ezviz",
            "uniview"

        ]

        for brand in brands:

            if brand in text:

                entity["brand"] = brand

        # -------------------------
        # Category
        # -------------------------

        categories = {

            "camera": [
                "camera",
                "cctv"
            ],

            "nvr": [
                "nvr"
            ],

            "dvr": [
                "dvr"
            ],

            "router": [
                "router"
            ],

            "switch": [
                "switch"
            ],

            "access point": [
                "access point",
                "wifi"
            ],

            "electrical": [
                "electric",
                "electrical",
                "wire",
                "switch board",
                "mcb"
            ]

        }

        for category, words in categories.items():

            for word in words:

                if word in text:

                    entity["category"] = category

        # -------------------------
        # Use Case
        # -------------------------

        use_cases = {

            "home": [
                "house",
                "home",
                "ghar"
            ],

            "office": [
                "office"
            ],

            "warehouse": [
                "warehouse"
            ],

            "shop": [
                "shop",
                "store"
            ],

            "hotel": [
                "hotel"
            ],

            "school": [
                "school"
            ],

            "hospital": [
                "hospital"
            ]

        }

        for usecase, words in use_cases.items():

            for word in words:

                if word in text:

                    entity["use_case"] = usecase

        return entity