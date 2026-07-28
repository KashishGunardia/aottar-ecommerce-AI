import re
import spacy

nlp = spacy.load("en_core_web_sm")


class EntityExtractor:

    BRANDS = {
        "auxo",
        "aottor",
        "dashglasses"
    }

    CATEGORIES = {

        "camera",
        "cctv",
        "switch",
        "lock",
        "doorbell",
        "light",
        "router",
        "sensor",
        "automation",
        "electrical",
        "wifi",
        "smart switch",
        "smart lock",
        "smart light"

    }

    USE_CASES = {

        "home",
        "house",
        "office",
        "shop",
        "hotel",
        "warehouse",
        "factory",
        "school",
        "hospital"

    }

    FEATURES = {

        "wifi",
        "wireless",
        "touch",
        "smart",
        "remote",
        "voice",
        "glass"

    }

    def extract(self, text):

        doc = nlp(text.lower())

        result = {

            "brand": None,
            "category": None,
            "budget": None,
            "use_case": None,
            "feature": [],
            "quantity": None

        }

        # -----------------------
        # Brand
        # -----------------------

        for token in doc:

            if token.text in self.BRANDS:
                result["brand"] = token.text

        # -----------------------
        # Category
        # -----------------------

        sentence = text.lower()

        for cat in self.CATEGORIES:

            if cat in sentence:
                result["category"] = cat
                break

        # -----------------------
        # Use Case
        # -----------------------

        for use in self.USE_CASES:

            if use in sentence:
                result["use_case"] = use
                break

        # -----------------------
        # Features
        # -----------------------

        for token in doc:
         if token.text in self.FEATURES:
           result["feature"].append(token.text)
        # -----------------------
        # Budget
        # -----------------------

        budget = re.search(r'(\d{3,7})', sentence)

        if budget:
            result["budget"] = int(budget.group())

        # -----------------------
        # Quantity
        # -----------------------

        quantity = re.search(
           r'(\d+)\s+(?:\w+\s+){0,3}?(camera|cameras|switch|switches|lock|locks|light|lights)',
      sentence
)

        if quantity:
          result["quantity"] = int(quantity.group(1))

        return result