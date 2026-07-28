from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()


class ResponseService:

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate(self, language, intent):

        prompt = f"""
You are Aottar's AI Shopping Assistant.

Reply ONLY in the following language:

{language}

Intent:

{intent}

Possible intents:

GREETING
GOODBYE
THANKS
ORDER
VENDOR
GENERAL
ABUSE

Rules:

GREETING:
Welcome the customer warmly.

Mention you help with:
• Smart Home
• CCTV
• Smart Switches
• Smart Locks
• Smart Lights
• Vendor Services

GOODBYE:
Say goodbye politely.

THANKS:
Reply politely.

ORDER:
Tell them you'll help track the order.

VENDOR:
Invite them to become a vendor.

GENERAL:
Tell them what Aottar can help with.

ABUSE:
Stay calm and professional.

Return ONLY the response.
"""

        return self.llm.invoke(
            [HumanMessage(content=prompt)]
        ).content.strip()