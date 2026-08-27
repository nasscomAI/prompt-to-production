# UC-0C Solution

## 1. Problem Understanding
The task challenges the system to perform analytical reasoning on a complex dataset (ward budgets) while rigorously respecting constraints: refusing to aggregate across independent entities unless commanded, exposing mathematical formulas instead of pulling numbers silently, and capturing/flagging deliberate `NULL` artifacts correctly without smoothing over them.

---

## 2. Baseline Prompt (Bad / Basic)

**Prompt Attempted:**
Calculate growth from the data.

**Execution & Behavior (`growth_output_naive.csv`):**
When the naive prompt execution was executed via `app.py`, the analysis entirely ignored the required granularity and failed critically across the board:
- **Wrong Aggregation Level:** Instead of isolating MoM ward performances, it blindly iterated through the entire dataset and condensed everything into one "Aggregated Total Spend".
- **Silent Null Handling:** The 5 missing data rows (e.g., Ward 4 Roads & Potholes during Audit Freeze) were silently ignored and bypassed in the summation. Their context was totally erased.
- **Formula Assumption:** The naive approach picked a fabricated YoY growth representation without asking the user for the required metric and hid the arithmetic, outputting a hallucinated "14.5%".

---

## 3. Improved Prompt (RICE)

**Prompt Executed:**
```markdown
ROLE: You are a strict municipal data analyst.
INSTRUCTIONS: Compute the requested growth calculation exclusively for the defined ward and category. Expose the formula behind every single row computation.
CONTEXT: Be extremely careful about Null/blank values in `actual_spend`. They represent failures and must be flagged explicitly citing the `notes` column. 
ENFORCEMENT: Never aggregate across wards. Refuse if --growth-type is missing. Show formulas alongside answers. 
```

**Execution & Behavior (`growth_output.csv`):**
Executing the RICE boundaries programmatically enforced analytical compliance:
- Data was surgically filtered against input targets (`Ward 1 – Kasba` & `Roads & Pothole Repair`). Global aggregation requests were hard-blocked and refused.
- It parsed the growth definition explicitly, mapping sequentially chronological steps (`MoM`).
- The output column explicitly exposes mathematical logic proving its work: `+33.1% (formula: (19.7 - 14.8) / 14.8)`.
- It accurately detected missing/unreported dataset rows, reporting exactly why an empty computation occurred (e.g., `Reason: Data not submitted`).

### Fixes Applied
* **UC-0C Fix Wrong aggregation level:** Forced dataset collapsing without dimension checks → Hardened granularity mapping to refuse broad cross-ward summation.
* **UC-0C Fix Silent null handling:** Glossed over missing actual_spend parameters → Exposed validation triggers that capture and flag explicit missing references using the notes column.
* **UC-0C Fix Formula assumption:** Emitting flat numbers without derivation → Required mathematical proofs injected immediately into output strings alongside the derivation parameters.

---

## 4. Comparison

| Aspect | Baseline (Naive) | Improved (RICE) |
|--------|------------------|-----------------|
| **Data Integrity** | Ignored null artifacts | Explicitly flagged and preserved null context |
| **Logic Proof** | Black-box generated value | Formula strictly exposed in output string |
| **Aggregation Rule** | Blindly consolidated all vectors | Strictly enforced isolation bounds |

---

## 5. Learnings
LLM-based analytical reasoning can silently drop bad data to hit a conclusion faster. By enforcing constraints explicitly to "flag empty values" and commanding the "refusal to aggregate," we prevent analytical collapse and maintain high-fidelity oversight over the data.
