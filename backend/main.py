from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import DisputeRequest, DisputeResponse, StageResult
from order_tool import OrderInspectionTool
from policy_store import PolicyRetriever
from eligibility import EligibilityEvaluator
from escalation import EscalationRouter
from config import GROQ_API_KEY

app = FastAPI(title="Refund Dispute Arbitrator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

order_tool = OrderInspectionTool()
policy_store = PolicyRetriever()
eligibility_evaluator = EligibilityEvaluator()
escalation_router = EscalationRouter()

# stage weights used to roll individual confidences into one project accuracy figure
STAGE_WEIGHTS = {
    "policy_retrieval": 0.20,
    "order_inspection": 0.15,
    "eligibility_evaluation": 0.35,
    "escalation_routing": 0.30,
}


@app.post("/api/resolve-dispute", response_model=DisputeResponse)
def resolve_dispute(request: DisputeRequest):
    order, order_confidence = order_tool.lookup(request.order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"No order found for {request.order_id}")

    filed_date = date.fromisoformat(request.filed_date)
    query = f"{order['category']} {request.reason}"
    matches, retrieval_confidence = policy_store.search(
        query,
        top_k=1,
        expected_category=order["category"],
    )
    best_policy = matches[0] if matches else {"text": "No matching policy found."}

    eligibility_result, eligibility_confidence = eligibility_evaluator.evaluate(
        order, filed_date, request.is_defective
    )
    escalation_result, escalation_confidence = escalation_router.route(
        order, request.claimed_amount, eligibility_result
    )

    explanation = _build_explanation(
        order, request.reason, escalation_result["decision"], best_policy["text"], eligibility_result
    )

    stages = [
        StageResult(name="policy_retrieval", output=best_policy, confidence=retrieval_confidence),
        StageResult(name="order_inspection", output=order, confidence=order_confidence),
        StageResult(name="eligibility_evaluation", output=eligibility_result, confidence=eligibility_confidence),
        StageResult(name="escalation_routing", output=escalation_result, confidence=escalation_confidence),
    ]

    overall_accuracy = round(
        sum(s.confidence * STAGE_WEIGHTS[s.name] for s in stages), 1
    )

    return DisputeResponse(
        order_id=request.order_id,
        decision=escalation_result["decision"],
        explanation=explanation,
        stages=stages,
        overall_accuracy=overall_accuracy,
    )


def _build_explanation(order, reason, decision, policy_text, eligibility):
    if not GROQ_API_KEY:
        return _fallback_explanation(order, decision, policy_text, eligibility)

    from agent import ExplanationAgent
    try:
        agent = ExplanationAgent()
        return agent.explain(order, reason, decision, policy_text, eligibility)
    except Exception:
        return _fallback_explanation(order, decision, policy_text, eligibility)


def _fallback_explanation(order, decision, policy_text, eligibility):
    if decision == "approved":
        return f"Your refund for {order['item_name']} has been approved. {policy_text}"
    if decision == "escalated":
        return (
            f"Your dispute for {order['item_name']} has been sent to our support team "
            f"for manual review due to the claim's value or dispute history."
        )
    return f"Your refund request for {order['item_name']} was denied. {policy_text}"


@app.get("/api/health")
def health():
    return {"status": "ok"}
