from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY, GROQ_MODEL

PROMPT = ChatPromptTemplate.from_template(
    """You are a customer support agent explaining a refund decision.
Keep it to 2-3 sentences, be polite and direct, and ground the explanation
in the policy clause given below. Do not invent policy details that aren't there.

Order item: {item_name}
Dispute reason: {reason}
Decision: {decision}
Relevant policy clause: {policy_text}
Days since delivery: {days_elapsed} (return window: {window} days)
"""
)


class ExplanationAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0.2)
        self.chain = PROMPT | self.llm

    def explain(self, order, reason, decision, policy_text, eligibility):
        response = self.chain.invoke({
            "item_name": order["item_name"],
            "reason": reason,
            "decision": decision,
            "policy_text": policy_text,
            "days_elapsed": eligibility["days_elapsed"],
            "window": eligibility["return_window_days"],
        })
        return response.content.strip()
