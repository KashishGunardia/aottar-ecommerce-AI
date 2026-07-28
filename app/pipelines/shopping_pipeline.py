from app.memory.conversation_memory import SessionMemoryStore
from app.retrieval.hybrid_search import HybridSearch
from app.retrieval.reranker import ProductReranker

from app.models.llm_classifier import LLMClassifier
from app.models.llm_entity_extractor import LLMEntityExtractor


class ShoppingPipeline:

    def __init__(self):

        self.classifier = LLMClassifier()
        self.extractor = LLMEntityExtractor()

        self.memory_store = SessionMemoryStore()

        self.hybrid = HybridSearch()
        self.reranker = ProductReranker()

    def run(self, message, session_key="default"):

        # ==========================================
        # Intent Classification
        # ==========================================

        intent = self.classifier.classify(message)

        print("=" * 60)
        print("MESSAGE :", message)
        print("INTENT  :", intent)
        print("=" * 60)

        # ==========================================
        # Greeting
        # ==========================================

        if intent == "GREETING":

            return {
                "intent": intent,
                "reply": (
                    "👋 Hello! Welcome to Aottar.\n\n"
                    "I'm your AI shopping assistant.\n\n"
                    "I can help you find:\n"
                    "• Smart Switches\n"
                    "• Smart Locks\n"
                    "• Smart Lights\n"
                    "• CCTV Cameras\n"
                    "• Home Automation\n"
                    "• Vendor Services\n\n"
                    "What are you looking for today?"
                ),
                "products": []
            }

        # ==========================================
        # General
        # ==========================================

        if intent == "GENERAL":

            return {
                "intent": intent,
                "reply": (
                    "I'm Aottar's AI assistant.\n\n"
                    "I can recommend products, compare models, "
                    "suggest smart home solutions, help you become a vendor, "
                    "or assist with order tracking.\n\n"
                    "Tell me what you need."
                ),
                "products": []
            }

        # ==========================================
        # Abuse
        # ==========================================

        if intent == "ABUSE":

            return {
                "intent": intent,
                "reply": (
                    "😊 I'm here to help.\n\n"
                    "Please tell me what you're looking for and "
                    "I'll do my best to assist you."
                ),
                "products": []
            }

        # ==========================================
        # Vendor
        # ==========================================

        if intent == "VENDOR":

            return {
                "intent": intent,
                "reply": (
                    "Great! We'd love to have you onboard.\n\n"
                    "Please share:\n"
                    "• Business Name\n"
                    "• Product Categories\n"
                    "• City\n"
                    "• GST (Optional)\n\n"
                    "Our onboarding team will contact you shortly."
                ),
                "products": []
            }

        # ==========================================
        # Order
        # ==========================================

        if intent == "ORDER":

            return {
                "intent": intent,
                "reply": (
                    "Sure!\n\n"
                    "Please share your Order ID or the mobile number "
                    "used while placing the order."
                ),
                "products": []
            }

        # ==========================================
        # Entity Extraction
        # ==========================================

        entities = self.extractor.extract(message)

        print("Entities:", entities)

        memory = self.memory_store.get_memory(session_key)

        memory.update(entities)

        entities = memory.merge(entities)

        print("Memory:", entities)

        # ==========================================
        # Build Search Query
        # ==========================================

        query = []

        if entities.get("brand"):
            query.append(entities["brand"])

        if entities.get("category"):
            query.append(entities["category"])

        if entities.get("feature"):
            query.extend(entities["feature"])

        if entities.get("use_case"):
            query.append(entities["use_case"])

        search_query = " ".join(query)

        print("Search Query:", search_query)

        # ==========================================
        # Hybrid Search
        # ==========================================

        products = self.hybrid.search(search_query)

        print(f"Retrieved {len(products)} products")

        # ==========================================
        # Budget Filter
        # ==========================================

        budget = entities.get("budget")

        filtered = []

        for p in products:

            try:
                price = int(float(p["price"]))
            except:
                continue

            if budget and price > budget:
                continue

            filtered.append(p)

        if not filtered:
            filtered = products

        # ==========================================
        # AI Re-ranking
        # ==========================================

        ranked = self.reranker.rerank(filtered, entities)

        # ==========================================
        # Final Reply
        # ==========================================

        if ranked:

            reply = f"I found {len(ranked)} product(s) matching your requirements."

        else:

            reply = (
                "Sorry, I couldn't find any matching products. "
                "Would you like me to suggest similar alternatives?"
            )

        return {
            "intent": intent,
            "reply": reply,
            "products": ranked[:5]
        }