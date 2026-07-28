from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

from app.utils.language_detector import LanguageDetector
from app.pipelines.shopping_pipeline import ShoppingPipeline


load_dotenv()



class ChatService:


    def __init__(self):

        self.pipeline = ShoppingPipeline()

        self.language_detector = LanguageDetector()


        self.llm = ChatGroq(

            model="llama-3.3-70b-versatile",

            temperature=0,

            api_key=os.getenv("GROQ_API_KEY")

        )



    # ------------------------------
    # Clean Response
    # ------------------------------

    def clean_response(self, text):

        text = text.replace("\\n", " ")

        text = text.replace("\n", " ")

        return " ".join(text.split())


        # ------------------------------
    # Response Builder
    # ------------------------------
    def build_response(
        self,
        message,
        response_type="text",
        products=None,
        quick_replies=None,
        actions=None,
        suggestions=None,
        metadata=None,
    ):
        return {
            "type": response_type,
            "message": self.clean_response(message),
            "products": products or [],
            "quick_replies": quick_replies or [],
            "actions": actions or [],
            "suggestions": suggestions or [],
            "metadata": metadata or {},
            "typing": False,
        }



    # ------------------------------
    # Greeting
    # ------------------------------

    def get_default_reply(self, language):

      replies = {

        "en": """
👋 Hello! Welcome to Aottar.

I'm your AI shopping assistant.

I can help you with:

• Smart Switches
• Smart Locks
• Smart Lights
• CCTV Cameras
• Home Automation
• Vendor Services

How can I help you today?
""",

        "hinglish": """
🙏 Namaste! Aottar mein aapka swagat hai.

Main aapka AI shopping assistant hoon.

Main aapki madad kar sakta hoon:

• Smart Switches
• Smart Locks
• Smart Lights
• CCTV Cameras
• Home Automation
• Vendor Services

Aaj main aapki kaise madad kar sakta hoon?
""",

        "hi": """
🙏 नमस्ते! Aottar में आपका स्वागत है।

मैं आपका AI शॉपिंग असिस्टेंट हूँ।

मैं आपकी मदद कर सकता हूँ:

• Smart Switches
• Smart Locks
• Smart Lights
• CCTV Cameras
• Home Automation
• Vendor Services

आज मैं आपकी कैसे सहायता कर सकता हूँ?
""",

        "mr": """
🙏 नमस्कार! Aottar मध्ये तुमचे स्वागत आहे.

मी तुमचा AI शॉपिंग सहाय्यक आहे.

मी मदत करू शकतो:

• Smart Switches
• Smart Locks
• Smart Lights
• CCTV Cameras
• Home Automation
• Vendor Services

आज मी तुमची कशी मदत करू शकतो?
"""
    }

      return self.clean_response(
        replies.get(language, replies["en"])
    )


    # ------------------------------
    # Product Relevance Filter
    # ------------------------------

    def is_relevant_product(self, product, message):


        query = message.lower()


        name = product.get(
            "name",
            ""
        ).lower()


        category = product.get(
            "category",
            ""
        ).lower()



        text = name + " " + category



        # Electrical queries

        if any(word in query for word in [

            "bijli",
            "electric",
            "power",
            "switch",
            "light",
            "current"

        ]):


            return any(word in text for word in [

                "switch",
                "light",
                "electrical",
                "automation"

            ])




        # CCTV queries

        if any(word in query for word in [

            "camera",
            "cctv",
            "security",
            "surveillance"

        ]):


            return any(word in text for word in [

                "camera",
                "cctv",
                "security"

            ])




        # Lock queries

        if any(word in query for word in [

            "lock",
            "door",
            "security lock"

        ]):


            return any(word in text for word in [

                "lock",
                "door lock"

            ])




        # Default

        return True




    # ------------------------------
    # Main Chat
    # ------------------------------

    def chat(self, message, session_key="default"):


        language = self.language_detector.detect(
            message
        )


        print(
            "Detected Language:",
            language
        )



        result = self.pipeline.run(
            message,
            session_key=session_key
        )



        products = result.get(
            "products",
            []
        )



        # ------------------------------
        # No Products
        # ------------------------------

        if not products:


            intent = result.get(
                "intent",
                "GENERAL"
            )


            if intent == "GREETING":

                return self.build_response(
                   message=self.get_default_reply(language),
                   response_type="greeting",
                   quick_replies=[
                         "Browse Products",
                         "Smart Switches",
                         "CCTV Cameras",
                         "Become a Vendor"
    ]
)

            return self.build_response(
                 message=result.get(
                 "reply",
                 "How can I help you?"
        ),
               response_type="text",
               suggestions=[
                   "Show CCTV",
                   "Smart Locks",
                   "Switches",
                   "Vendor Registration"
        ]
    )

        # ------------------------------
        # Filter Products
        # ------------------------------

        filtered_products = []


        for product in products:


            if self.is_relevant_product(
                product,
                message
            ):

                filtered_products.append(
                    product
                )



        # fallback

        if not filtered_products:

            filtered_products = products[:2]



        products = filtered_products[:3]



        # ------------------------------
        # Product Context
        # ------------------------------

        product_text = ""



        for p in products:


            product_text += f"""

Name:
{p.get('name')}

Price:
₹{p.get('price')}

Category:
{p.get('category')}

Brand:
{p.get('brand')}

"""



        prompt = f"""

You are Aottar's AI Shopping Assistant.


Reply in the same language as customer.


Customer:

{message}


Products:

{product_text}



Rules:

- Recommend only relevant products.
- Do not suggest unrelated products.
- Mention price.
- Explain why the product solves the customer's problem.
- Never invent specifications.
- Never create products.
- Keep reply under 120 words.
- End by asking if the customer needs more options.

"""



        answer = self.llm.invoke(

            [
                HumanMessage(
                    content=prompt
                )
            ]

        ).content



        return {


            "message":

            self.clean_response(
                answer
            ),


            "products": products

        }