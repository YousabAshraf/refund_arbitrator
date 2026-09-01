const API_BASE = "http://localhost:8000";


const form = document.getElementById("dispute-form");
const resultSection = document.getElementById("result");
const placeholder = document.getElementById("placeholder");
const errorBox = document.getElementById("form-error");
const submitBtn = document.getElementById("submit-btn");
const filedDateInput = document.getElementById("filed_date");

// Prevent future claim dates at the HTML-input level.
filedDateInput.max = new Date().toISOString().split("T")[0];

const STAGE_LABELS = {
  policy_retrieval: "Policy retrieval",
  order_inspection: "Order inspection",
  eligibility_evaluation: "Eligibility check",
  escalation_routing: "Escalation routing",
};

const STAMP_TEXT = {
  approved: "CLAIM\nAPPROVED",
  denied: "CLAIM\nDENIED",
  escalated: "SENT TO\nREVIEW",
};

/* ---------------- Backend health check ---------------- */

async function checkHealth() {
  const dot = document.getElementById("api-status");
  const label = document.getElementById("api-status-label");
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error();
    dot.className = "status-dot online";
    label.textContent = "Arbitrator online";
  } catch {
    dot.className = "status-dot offline";
    label.textContent = "Backend unreachable — start it on :8000";
  }
}
checkHealth();

/* ---------------- Form submit ---------------- */

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorBox.textContent = "";

  const payload = {
    order_id: document.getElementById("order_id").value,
    reason: document.getElementById("reason").value.trim(),
    claimed_amount: parseFloat(document.getElementById("claimed_amount").value),
    filed_date: document.getElementById("filed_date").value,
    is_defective: document.getElementById("is_defective").checked,
  };

  if (!payload.order_id) {
    errorBox.textContent = "Select the order this claim is about.";
    return;
  }
  if (payload.reason.length < 10 || payload.reason.length > 500) {
    errorBox.textContent = "Reason must be between 10 and 500 characters.";
    return;
  }
  if (Number.isNaN(payload.claimed_amount) || payload.claimed_amount <= 0) {
    errorBox.textContent = "Enter a valid claimed amount.";
    return;
  }
  if (payload.claimed_amount > 10000) {
    errorBox.textContent = "Claimed amount must be $10,000 or less.";
    return;
  }
  if (!payload.filed_date) {
    errorBox.textContent = "Select the date the claim was filed.";
    return;
  }
  if (payload.filed_date > filedDateInput.max) {
    errorBox.textContent = "Filed date cannot be in the future.";
    return;
  }

  submitBtn.disabled = true;
  submitBtn.classList.add("loading");
  submitBtn.querySelector(".btn-label").textContent = "Reviewing…";

  try {
    const res = await fetch(`${API_BASE}/api/resolve-dispute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "The claims desk couldn't process that order.");
    }

    const data = await res.json();
    renderResult(data);
  } catch (err) {
    errorBox.textContent = err.message.includes("fetch")
      ? "Can't reach the arbitrator backend. Is it running on localhost:8000?"
      : err.message;
  } finally {
    submitBtn.disabled = false;
    submitBtn.classList.remove("loading");
    submitBtn.querySelector(".btn-label").textContent = "Submit claim";
  }
});

/* ---------------- Rendering ---------------- */

function renderResult(data) {
  placeholder.hidden = true;
  resultSection.hidden = false;
  resultSection.dataset.decision = data.decision;

  const stamp = document.getElementById("stamp");
  stamp.className = "stamp";
  stamp.classList.remove("settled");
  void stamp.offsetWidth; // restart animation on repeat submissions

  document.getElementById("stamp-text").textContent =
    STAMP_TEXT[data.decision] || data.decision.toUpperCase();

  requestAnimationFrame(() => {
    stamp.classList.add(data.decision, "settled");
  });

  document.getElementById("case-id").textContent =
    `Case ${data.order_id} · filed ${new Date().toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}`;
  document.getElementById("explanation").textContent = data.explanation;

  const body = document.getElementById("ledger-body");
  body.innerHTML = "";
  for (const stage of data.stages) {
    body.appendChild(buildLedgerRow(stage));
  }

  document.getElementById("overall-score").textContent = `${data.overall_accuracy}%`;
  const circumference = 169.6;
  const offset = circumference * (1 - Math.min(data.overall_accuracy, 100) / 100);
  const dial = document.getElementById("dial-progress");
  dial.style.strokeDashoffset = circumference;
  requestAnimationFrame(() => {
    dial.style.strokeDashoffset = offset;
  });

  resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function buildLedgerRow(stage) {
  const row = document.createElement("tr");

  const nameCell = document.createElement("td");
  nameCell.className = "stage-name";
  nameCell.textContent = STAGE_LABELS[stage.name] || stage.name;

  const detailCell = document.createElement("td");
  detailCell.className = "stage-detail";
  detailCell.textContent = summarizeOutput(stage.name, stage.output);

  const confidenceCell = document.createElement("td");
  confidenceCell.className = "confidence-cell";
  confidenceCell.innerHTML = `
    <div class="meter"><div class="meter-fill" style="width:${stage.confidence}%"></div></div>
    <span class="meter-label">${stage.confidence}%</span>
  `;

  row.append(nameCell, detailCell, confidenceCell);
  return row;
}

function summarizeOutput(stageName, output) {
  switch (stageName) {
    case "policy_retrieval":
      return output.text || "No clause matched";
    case "order_inspection":
      return `${output.item_name} · $${output.purchase_amount} · delivered ${output.delivery_date}`;
    case "eligibility_evaluation":
      return output.eligible
        ? `Within window (${output.days_elapsed}/${output.return_window_days} days)`
        : `Outside window (${output.days_elapsed}/${output.return_window_days} days)`;
    case "escalation_routing":
      return output.high_value_flag
        ? "Routed for review — claim exceeds $500"
        : output.repeat_dispute_flag
        ? "Routed for review — repeat dispute history"
        : `Auto-${output.decision}`;
    default:
      return JSON.stringify(output);
  }
}
