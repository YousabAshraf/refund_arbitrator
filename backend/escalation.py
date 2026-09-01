from config import HIGH_VALUE_THRESHOLD, PRIOR_DISPUTE_THRESHOLD


class EscalationRouter:
    def route(self, order: dict, claimed_amount: float, eligibility: dict):
        high_value = claimed_amount > HIGH_VALUE_THRESHOLD
        repeat_offender = order.get("prior_disputes", 0) >= PRIOR_DISPUTE_THRESHOLD

        if high_value or repeat_offender:
            decision = "escalated"
        elif eligibility["eligible"]:
            decision = "approved"
        else:
            decision = "denied"

        result = {
            "decision": decision,
            "high_value_flag": high_value,
            "repeat_dispute_flag": repeat_offender,
        }

        confidence = self._confidence(claimed_amount, order.get("prior_disputes", 0))
        return result, confidence

    @staticmethod
    def _confidence(claimed_amount: float, prior_disputes: int) -> float:
        # amounts sitting right next to the $500 line are the borderline calls
        amount_gap = abs(claimed_amount - HIGH_VALUE_THRESHOLD) / HIGH_VALUE_THRESHOLD
        amount_confidence = 60 + min(amount_gap, 1.0) * 40

        dispute_gap = abs(prior_disputes - PRIOR_DISPUTE_THRESHOLD)
        dispute_confidence = 70 + min(dispute_gap, 3) * 10

        confidence = min(amount_confidence, dispute_confidence, 99.0)
        return round(confidence, 1)
