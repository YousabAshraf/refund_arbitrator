import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# deterministic return windows in days, keyed by product category
RETURN_WINDOW_DAYS = {
    "electronics": 15,
    "clothing": 45,
    "appliances": 30,
    "general": 30,
    "final_sale": 0,
}

DEFECTIVE_WINDOW_DAYS = 90

# escalation thresholds
HIGH_VALUE_THRESHOLD = 500.0
PRIOR_DISPUTE_THRESHOLD = 2

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
