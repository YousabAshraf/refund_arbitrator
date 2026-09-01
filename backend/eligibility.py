from datetime import date
from config import RETURN_WINDOW_DAYS, DEFECTIVE_WINDOW_DAYS


class EligibilityEvaluator:
    def evaluate(self, order: dict, filed_date: date, is_defective: bool):
        delivery_date = date.fromisoformat(order["delivery_date"])
        days_elapsed = (filed_date - delivery_date).days

        if is_defective:
            window = DEFECTIVE_WINDOW_DAYS
        else:
            window = RETURN_WINDOW_DAYS.get(order["category"], RETURN_WINDOW_DAYS["general"])

        eligible = 0 <= days_elapsed <= window
        margin = window - days_elapsed  # positive = days remaining, negative = days over

        result = {
            "eligible": eligible,
            "days_elapsed": days_elapsed,
            "return_window_days": window,
            "days_margin": margin,
        }

        confidence = self._confidence(margin, window)
        return result, confidence

    @staticmethod
    def _confidence(margin: int, window: int) -> float:
        # cases right on the boundary are the ones a human would double check,
        # so confidence dips the closer the claim sits to the cutoff day.
        if window == 0:
            return 100.0
        closeness = abs(margin) / window
        confidence = 60 + min(closeness, 1.0) * 40
        return round(min(confidence, 99.0), 1)
