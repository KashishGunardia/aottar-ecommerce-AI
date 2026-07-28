from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()


class LLMClassifier:

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.greetings = {
            "hi", "hello", "hey", "hii", "helo",
            "good morning", "good evening", "good afternoon",
            "namaste", "namaskar", "hola"
        }

        self.general = {
            "nice", "good", "great", "awesome", "cool",
            "ok", "okay", "fine", "thanks", "thank you",
            "thx", "super", "perfect", "amazing"
        }

    def classify(self, text):

        message = text.lower().strip()

        # -------------------------
        # Rule-based classification
        # -------------------------

        if message in self.greetings:
            return "GREETING"

        if message in self.general:
            return "GENERAL"

        # -------------------------
        # LLM Classification
        # -------------------------

        prompt = f"""
You are the intent classifier for Aottar.

Classify the customer's message into EXACTLY ONE of these labels:

GREETING
PRODUCT
USE_CASE
ORDER
VENDOR
GENERAL
ABUSE

Definitions:

GREETING:
Only when the customer starts the conversation or greets.

Examples:
hello
hi
hey
good morning
namaste

PRODUCT:
Customer asks for a specific product, brand, model, comparison or price.

Examples:
Need smart switch
Need CCTV
Need smart lock
Camera under 5000

USE_CASE:
Customer explains a problem or requirement.

Examples:
Bijli ki problem hai
Need security for office
Parents stay alone
Need automation
Ghar mein andhera hai

ORDER:
Track order
Refund
Return
Replacement
Shipment

VENDOR:
Become vendor
Seller registration
Partnership

ABUSE:
Offensive language.

GENERAL:
General conversation, appreciation or unrelated chat.

Examples:
nice
good
great
thanks
okay
awesome

Return ONLY ONE LABEL.

Customer:
{text}
"""

        return (
            self.llm.invoke([HumanMessage(content=prompt)])
            .content
            .strip()
            .upper()
        )