import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()


class LLMEntityExtractor:

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def extract(self, text):

        prompt = f"""
Extract shopping entities from the customer query.

Return ONLY valid JSON.

Schema:

{{
    "brand": "",
    "category": "",
    "budget": null,
    "quantity": null,
    "use_case": "",
    "features": []
}}

Customer:

{text}
"""

        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        ).content

        try:
            return json.loads(response)
        except Exception:
            return {
                "brand": None,
                "category": None,
                "budget": None,
                "quantity": None,
                "use_case": None,
                "features": []
            }