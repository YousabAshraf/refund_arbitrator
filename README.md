# Adaptive E-Commerce Customer Dispute & Refund Arbitrator

An automated claims resolution assistant that reconciles customer refund
and return disputes against store policy documents and purchase
transaction records.

Operating on an **Agentic RAG (Retrieval-Augmented Generation)**
workflow, the system retrieves relevant return and warranty clauses,
inspects order records, deterministically evaluates eligibility windows,
and decides whether to approve a refund, deny the claim, or escalate
high-risk cases to human review.

------------------------------------------------------------------------

## 🚀 Key AI & Tool Capabilities

-   **Policy Vector Retrieval:** Indexes store refund and warranty
    policies in a FAISS vector database and retrieves relevant policy
    clauses using HuggingFace Embeddings.

-   **Order Inspection Tool:** Queries mock order records from
    `orders.json` to retrieve delivery dates, purchase amounts, product
    categories, item conditions, and dispute history.

-   **Eligibility Evaluator:** Calculates the elapsed time between order
    delivery and dispute filing dates, then evaluates eligibility
    against category-specific return windows and defective-item
    policies.

-   **Autonomous Escalation Router:** Applies deterministic business
    rules to identify high-risk cases, including claims exceeding the
    `$500` threshold and customers with repeated dispute history,
    routing them to human review.

-   **Confidence Scoring:** Generates stage-level confidence scores for
    policy retrieval, order inspection, eligibility evaluation, and
    escalation routing, along with an overall weighted confidence score.

-   **LLM-Powered Explanations:** Optionally uses Groq through LangChain
    to generate clear customer-facing explanations while keeping the
    core business decisions deterministic.

------------------------------------------------------------------------

## 🛠️ Tech Stack

**AI & Agent Core:** - Python 3.x - LangChain - FAISS Vector Store -
HuggingFace Embeddings (`all-MiniLM-L6-v2`) - Groq API

**Backend:** - FastAPI - Pydantic - Python `datetime` - REST API

**Frontend:** - Vanilla JavaScript (`app.js`) - HTML5 (`index.html`) -
CSS3 (`style.css`)

------------------------------------------------------------------------

## 📂 Project Structure

``` text
refund_arbitrator/
├── backend/
│   ├── data/
│   │   ├── orders.json        # Mock database for customer orders
│   │   └── policies.json      # Store refund and warranty policies
│   ├── agent.py               # LangChain + Groq explanation generation
│   ├── config.py              # Application configuration and thresholds
│   ├── eligibility.py         # Refund eligibility and date evaluation
│   ├── escalation.py          # High-risk and repeat-dispute routing
│   ├── main.py                # FastAPI application entry point
│   ├── order_tool.py          # Order inspection and data retrieval
│   ├── policy_store.py        # FAISS vector store and policy retrieval
│   └── schemas.py             # Pydantic request/response models
├── frontend/
│   ├── app.js                 # UI interactions and API requests
│   ├── index.html             # Main web interface
│   └── style.css              # Frontend styling
├── tests/
│   ├── conftest.py
│   ├── test_eligibility.py    # Eligibility rule tests
│   └── test_escalation.py     # Escalation rule tests
├── requirements.txt           # Python dependencies
├── .gitignore                 # Ignored files and secrets
└── README.md                  # Project documentation
```

------------------------------------------------------------------------

## 🔄 Decision Workflow

``` text
Customer Dispute
       │
       ▼
Policy Vector Retrieval
       │
       ▼
Order Inspection
       │
       ▼
Eligibility Evaluation
       │
       ▼
Escalation Router
       │
   ┌───┼───────────┐
   ▼   ▼           ▼
Approve Deny    Escalate
                 │
                 ▼
           Human Review
```

------------------------------------------------------------------------

## 📡 API

### Resolve Dispute

``` http
POST /api/resolve-dispute
```

Example request:

``` json
{
  "order_id": "ORD-1001",
  "reason": "The item stopped working after two weeks",
  "claimed_amount": 79.99,
  "filed_date": "2025-02-15",
  "is_defective": false
}
```

### Health Check

``` http
GET /api/health
```

------------------------------------------------------------------------

## ⚙️ Configuration

The Groq integration is optional.

Set the API key using an environment variable:

``` env
GROQ_API_KEY=your_api_key_here
```

The application automatically falls back to deterministic explanations
when the API key is unavailable or the LLM request fails.

> **Security:** Never commit API keys or `.env` files to the repository.

------------------------------------------------------------------------

## 🎯 Decision Outcomes

-   **Approved:** The claim satisfies the applicable refund policy and
    does not trigger escalation rules.
-   **Denied:** The claim does not satisfy the applicable eligibility
    requirements.
-   **Escalated:** The claim is considered high-risk or requires human
    investigation.

------------------------------------------------------------------------

## 📊 Confidence Model

The system calculates an overall confidence score using weighted stage
results:

  Stage                      Weight
  ------------------------ --------
  Policy Retrieval              20%
  Order Inspection              15%
  Eligibility Evaluation        35%
  Escalation Routing            30%

The resulting `overall_accuracy` is a pipeline confidence indicator and
should not be interpreted as measured production accuracy.

------------------------------------------------------------------------

## ▶️ Running the Project

### Backend

``` powershell
cd backend
pip install -r ..\requirements.txt
uvicorn main:app --reload
```

Backend:

``` text
http://localhost:8000
```

### Frontend

Open a second terminal:

``` powershell
cd frontend
python -m http.server 5500
```

Frontend:

``` text
http://localhost:5500
```

------------------------------------------------------------------------

## 🔮 Future Improvements

-   Real e-commerce platform integration
-   Production database integration
-   Real payment and refund APIs
-   Authentication and authorization
-   Human support dashboard
-   Advanced fraud detection
-   Multi-store policy management
-   Case history and dispute tracking
-   Advanced risk scoring
-   Multi-language support
-   Production monitoring and analytics

------------------------------------------------------------------------
