import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAQ_FILE = os.path.join(BASE_DIR, "data", "company_faq.json")


class FAQService:

    def __init__(self):
        with open(FAQ_FILE, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def search(self, question: str):

        question = question.lower()

        if "about" in question or "company" in question:
            return self.data["company"]["about"]

        if "mission" in question:
            return self.data["company"]["mission"]

        if "vision" in question:
            return self.data["company"]["vision"]

        if "installation" in question:
            return self.data["services"]["installation"]

        if "shipping" in question:
            return self.data["shipping"]["availability"]

        if "return" in question:
            return self.data["returns"]["policy"]

        if "support" in question:
            return self.data["services"]["support"]

        if "contact" in question or "email" in question:
            return (
                f"Email: {self.data['contact']['email']}\n"
                f"Website: {self.data['contact']['website']}"
            )

        return None