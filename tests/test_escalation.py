from escalation import EscalationRouter


def test_high_value_claim_escalates_even_if_eligible():
    router = EscalationRouter()
    order = {"prior_disputes": 0}

    result, confidence = router.route(order, claimed_amount=600.0, eligibility={"eligible": True})

    assert result["decision"] == "escalated"
    assert result["high_value_flag"] is True
    assert result["repeat_dispute_flag"] is False
    assert confidence == 68.0


def test_repeat_dispute_escalates_even_if_low_value():
    router = EscalationRouter()
    order = {"prior_disputes": 2}

    result, confidence = router.route(order, claimed_amount=100.0, eligibility={"eligible": True})

    assert result["decision"] == "escalated"
    assert result["high_value_flag"] is False
    assert result["repeat_dispute_flag"] is True
    assert confidence == 70.0


def test_eligible_non_flagged_claim_is_approved():
    router = EscalationRouter()
    order = {"prior_disputes": 0}

    result, _ = router.route(order, claimed_amount=200.0, eligibility={"eligible": True})

    assert result["decision"] == "approved"


def test_ineligible_non_flagged_claim_is_denied():
    router = EscalationRouter()
    order = {"prior_disputes": 1}

    result, _ = router.route(order, claimed_amount=120.0, eligibility={"eligible": False})

    assert result["decision"] == "denied"
