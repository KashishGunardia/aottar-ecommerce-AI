from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()


class KnowledgeEngine:

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def answer(self, question, context=""):

        prompt = f"""
You are Aottar's Technical Product Expert.

Answer ONLY if the question is related to:

- CCTV
- Smart Locks
- Smart Switches
- Home Automation
- Electrical Products
- Networking
- Smart Doorbells

Context:
{context}

Customer Question:
{question}

Rules:

- Keep the answer under 150 words.
- Be technically correct.
- Never invent specifications.
- If the information is unavailable, clearly say so.
- Recommend checking the product page when appropriate.
"""

        return self.llm.invoke(
            [HumanMessage(content=prompt)]
        ).content