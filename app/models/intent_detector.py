from sentence_transformers import SentenceTransformer, util


class IntentDetector:

    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.examples = {

            "GREETING": [
                "hello",
                "hi",
                "hey",
                "namaste"
            ],

            "ORDER": [
                "track my order",
                "cancel my order",
                "refund"
            ],

            "VENDOR": [
                "become vendor",
                "seller registration"
            ],

            "FAQ": [
                "delivery",
                "shipping",
                "warranty",
                "installation"
            ],

            "PRODUCT": [
                "camera",
                "cctv",
                "router",
                "switch",
                "electrical",
                "networking",
                "dahua",
                "hikvision"
            ]

        }

        self.intent_embeddings = {}

        for intent, examples in self.examples.items():

            self.intent_embeddings[intent] = self.model.encode(
                examples,
                convert_to_tensor=True
            )

    def predict(self, message):

        embedding = self.model.encode(
            message,
            convert_to_tensor=True
        )

        best_score = -1
        best_intent = "UNRELATED"

        for intent, vectors in self.intent_embeddings.items():

            score = util.cos_sim(
                embedding,
                vectors
            ).max().item()

            if score > best_score:

                best_score = score
                best_intent = intent

        return best_intent