import json
from config import DATA_DIR
import os

REQUIRED_FIELDS = [
    "order_id", "customer_id", "item_name", "category",
    "purchase_amount", "delivery_date", "item_condition", "prior_disputes",
]


class OrderInspectionTool:
    def __init__(self):
        path = os.path.join(DATA_DIR, "orders.json")
        with open(path) as f:
            orders = json.load(f)
        self._orders = {o["order_id"]: o for o in orders}

    def lookup(self, order_id: str):
        order = self._orders.get(order_id)
        if order is None:
            return None, 0.0

        present = sum(1 for field in REQUIRED_FIELDS if order.get(field) not in (None, ""))
        confidence = round(100 * present / len(REQUIRED_FIELDS), 1)
        return order, confidence
