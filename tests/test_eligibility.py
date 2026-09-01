from datetime import date

from eligibility import EligibilityEvaluator


def test_non_defective_within_category_window_is_eligible():
    evaluator = EligibilityEvaluator()
    order = {"category": "electronics", "delivery_date": "2026-08-01"}

    result, confidence = evaluator.evaluate(order, filed_date=date(2026, 8, 11), is_defective=False)

    assert result["eligible"] is True
    assert result["days_elapsed"] == 10
    assert result["return_window_days"] == 15
    assert result["days_margin"] == 5
    assert confidence == 73.3


def test_non_defective_outside_window_is_denied():
    evaluator = EligibilityEvaluator()
    order = {"category": "electronics", "delivery_date": "2026-08-01"}

    result, confidence = evaluator.evaluate(order, filed_date=date(2026, 8, 17), is_defective=False)

    assert result["eligible"] is False
    assert result["days_elapsed"] == 16
    assert result["return_window_days"] == 15
    assert result["days_margin"] == -1
    assert confidence == 62.7


def test_defective_uses_defective_window():
    evaluator = EligibilityEvaluator()
    order = {"category": "final_sale", "delivery_date": "2026-06-01"}

    result, confidence = evaluator.evaluate(order, filed_date=date(2026, 8, 20), is_defective=True)

    assert result["eligible"] is True
    assert result["days_elapsed"] == 80
    assert result["return_window_days"] == 90
    assert result["days_margin"] == 10
    assert confidence == 64.4


def test_confidence_for_zero_window_returns_100():
    assert EligibilityEvaluator._confidence(margin=0, window=0) == 100.0
