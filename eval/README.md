# Automated Evaluation Benchmark Harness

The evaluation harness provides automated regression and enforcement verification across all Use Cases (`UC-0A` through `UC-0D`).

---

## What It Evaluates

1. **UC-0A (Complaint Classifier)**
   - **Severity Accuracy:** Verifies 100% detection of critical trigger keywords (`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`) categorized as `Urgent`.
   - **Taxonomy Enforcement:** Validates that 100% of rows use only the 9 allowed categories.
   - **Audit Reasons:** Verifies that no rows are missing rationale citations.

2. **UC-0B (Summary Meaning Preservation)**
   - **Condition Retention:** Ensures dual approval requirements (e.g. Leave Without Pay approved by Department Head AND HR Director) are not dropped during summarization.

3. **UC-0C (Ward Budget Calculation)**
   - **Granularity:** Enforces per-ward and per-category breakdowns (rejects naive single aggregated numbers).
   - **Data Hygiene:** Flags any unhandled `NaN` or null values in computed datasets.

4. **UC-0D (Civic Budget Allocation & Dual-Signature)**
   - **Dual Sign-Off Gate:** Confirms that multi-signature rules correctly reject unauthorized project proposals.
   - **Overdraft Gate:** Confirms that project requests exceeding remaining ward balances are blocked.

---

## How to Run

From the repository root:

```bash
python eval/eval_harness.py
```
