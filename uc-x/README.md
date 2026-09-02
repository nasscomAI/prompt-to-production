# UC-X — Ask My Documents

**Core Failure Modes Addressed:** Cross-document blending · Hedged hallucination · Condition dropping

---

## 📂 Files Overview

| File | Purpose |
|---|---|
| [agents.md](./agents.md) | Q&A agent persona, single-source boundary, and RICE enforcement rules. |
| [skills.md](./skills.md) | Standardized skill definitions (`retrieve_documents`, `answer_question`). |
| [app.py](./app.py) | Python policy Q&A agent enforcing single-source attribution and refusal templates. |

---

## 🚀 How to Run

### Interactive CLI Mode
```bash
# From uc-x/
python app.py

# Or from project root
python uc-x/app.py
```

### Non-Interactive Single Question Mode
```bash
python uc-x/app.py --question "Can I use my personal phone to access work files when working from home?"
```

---

## 🛑 Standard Refusal Template

When a question is not directly covered in the documents, the system issues this exact response without hedging:
```
This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant department] for guidance.
```

---

## 📋 The 7 Verified Test Questions

| Question | Source Document | Section Citation | Expected Behavior |
|---|---|---|---|
| **"Can I carry forward unused annual leave?"** | `policy_hr_leave.txt` | Section 2 (2.6 & 2.7) | Max 5 days, forfeited 31 Dec, must use Jan–Mar. |
| **"Can I install Slack on my work laptop?"** | `policy_it_acceptable_use.txt` | Section 2 (2.3 & 2.4) | Requires written IT approval & CMC catalogue. |
| **"What is the home office equipment allowance?"** | `policy_finance_reimbursement.txt` | Section 3 (3.1 & 3.2) | ₹8,000 one-time allowance for permanent WFH only. |
| **"Can I use my personal phone for work files from home?"** | `policy_it_acceptable_use.txt` | Section 3 (3.1 & 3.2) | **Single-source IT answer** (email & portal only; no work files). **No cross-doc blend!** |
| **"What is the company view on flexible working culture?"** | None | None | **Exact Refusal Template** returned. |
| **"Can I claim DA and meal receipts on the same day?"** | `policy_finance_reimbursement.txt` | Section 2 (2.6) | **No**, explicitly prohibited simultaneously. |
| **"Who approves leave without pay?"** | `policy_hr_leave.txt` | Section 5 (5.2 & 5.3) | **Dept Head AND HR Director**; >30 days requires Municipal Commissioner. |

---

## 🛠 Skills Defined in `skills.md`

1. **`retrieve_documents`**: Ingests and hierarchically indexes all policy texts.
2. **`answer_question`**: Resolves questions against a single document with exact section citations or executes the refusal template.

---

## 📝 Commit Message Formula

```bash
UC-X Fix [failure mode]: [why it failed] → [what you changed]
```

**Example:**
`UC-X Fix cross-doc blending: no single-source rule → added single-source attribution enforcement and refusal template`
