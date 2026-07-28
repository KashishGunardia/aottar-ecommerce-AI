import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.rag.retriever import get_retriever
from app.services.intent_service import IntentService
from app.services.recommendation_service import RecommendationService
from app.services.category_service import CategoryService


load_dotenv()



class AIService:


    def __init__(self):

        self.retriever = get_retriever()

        self.intent = IntentService()

        self.recommendation = RecommendationService()

        self.category = CategoryService()


        self.llm = ChatGroq(

            model="llama-3.3-70b-versatile",

            temperature=0.3,

            api_key=os.getenv("GROQ_API_KEY")

        )



    # ---------------------------------
    # Clean AI Response
    # ---------------------------------

    def clean_response(self, text):

        text = text.replace("\\n", " ")

        text = text.replace("\n", " ")

        return " ".join(text.split())



    def get_response(self, message: str):


        message = message.strip()


        intent = self.intent.classify(message).strip().upper()


        print(
            f"\nDetected Intent : {intent}\n"
        )



        # ==========================================
        # GREETING
        # ==========================================


        if intent == "GREETING":


            prompt = f"""

You are Aottar AI.

You are the official AI assistant of Aottar.

Welcome the customer warmly.

Mention that you help with:

• CCTV
• Security
• Networking
• Smart Home
• Electrical
• Industrial Products

Keep the answer below 35 words.

Customer:
{message}

"""


            answer = self.llm.invoke(prompt)


            return {


                "reply": self.clean_response(
                    answer.content
                ),


                "products": []

            }





        # ==========================================
        # SMALL TALK
        # ==========================================


        if intent == "SMALL_TALK":


            prompt = f"""

Reply naturally.

Tell the customer that you can help with:

Product Recommendation

Product Comparison

Technical Guidance

Pricing

Shopping


Maximum 35 words.


Customer:
{message}

"""


            answer = self.llm.invoke(prompt)



            return {


                "reply": self.clean_response(
                    answer.content
                ),


                "products": []

            }





        # ==========================================
        # FAQ
        # ==========================================


        if intent == "FAQ":


            return {


                "reply":

                "I'd be happy to help. Please ask anything about delivery, warranty, installation, payment, returns, shipping or product support.",


                "products": []

            }





        # ==========================================
        # ORDER
        # ==========================================


        if intent == "ORDER":


            return {


                "reply":

                "Sure! Please share your Order ID so I can check your order status.",


                "products": []

            }





        # ==========================================
        # VENDOR
        # ==========================================


        if intent == "VENDOR":


            return {


                "reply":

                "That's great! We'd love to have you onboard. Register your business, upload products and start selling across India. Would you like to know the vendor onboarding process?",


                "products": []

            }





        # ==========================================
        # USE CASE RECOMMENDATION
        # ==========================================


        use_case = self.recommendation.detect_use_case(message)



        if use_case:


            categories = self.category.get_categories(use_case)


            category_query = " ".join(categories)



            docs = self.retriever.invoke(
                category_query
            )



            products = []

            context = ""



            for doc in docs:



                context += f"""

Product:
{doc.metadata.get('name')}

Category:
{doc.metadata.get('category')}

Price:
₹{doc.metadata.get('price')}

Description:
{doc.page_content}

"""



                products.append({


                    "name":
                    doc.metadata.get("name"),


                    "price":
                    doc.metadata.get("price"),


                    "url":
                    doc.metadata.get("url"),


                    "image":
                    doc.metadata.get("image")


                })





            prompt = f"""

You are Aottar AI.

The customer is planning a {use_case.lower()}.

Recommend these categories:

{", ".join(categories)}


Use ONLY the provided products.


{context}


Keep the answer below 70 words.


End with a question asking which category they'd like to explore.

"""



            answer = self.llm.invoke(prompt)



            return {


                "reply":

                self.clean_response(
                    answer.content
                ),


                "products": products

            }





        # ==========================================
        # PRODUCT SEARCH
        # ==========================================


        docs = self.retriever.invoke(
            message
        )



        if not docs:


            return {


                "reply":

                "I'm here to help you find the right products on Aottar. You can ask about CCTV cameras, networking devices, smart home automation, electrical products, IT equipment, product comparisons, pricing, or becoming a vendor.",


                "products": []

            }





        products = []

        context = ""



        for doc in docs:



            context += f"""

Product Name:
{doc.metadata.get('name')}

Category:
{doc.metadata.get('category')}

Brand:
{doc.metadata.get('brand')}

Price:
₹{doc.metadata.get('price')}

Description:
{doc.page_content}

"""



            products.append({


                "name":

                doc.metadata.get("name"),


                "price":

                doc.metadata.get("price"),


                "url":

                doc.metadata.get("url"),


                "image":

                doc.metadata.get("image")


            })





        prompt = f"""

You are Aottar AI.

You are a professional shopping assistant.


Answer ONLY using the products provided below.


Rules:

- Never invent products.
- Never invent prices.
- Never invent specifications.
- Recommend the most suitable product first.
- Explain WHY it suits the customer's needs.
- If multiple products fit, compare briefly.
- Keep the answer below 80 words.
- End by asking if the customer would like more details.


Customer Question:

{message}


Available Products:

{context}

"""



        answer = self.llm.invoke(prompt)



        return {


            "reply":

            self.clean_response(
                answer.content
            ),


            "products": products

        }