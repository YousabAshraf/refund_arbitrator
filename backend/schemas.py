from pydantic import BaseModel, Field


class DisputeRequest(BaseModel):
    order_id: str
    reason: str
    claimed_amount: float
    filed_date: str  # YYYY-MM-DD
    is_defective: bool = False


class StageResult(BaseModel):
    name: str
    output: dict
    confidence: float  # 0-100


class DisputeResponse(BaseModel):
    order_id: str
    decision: str  # approved / denied / escalated
    explanation: str
    stages: list[StageResult]
    overall_accuracy: float
