# UC-0D — Civic Budget Allocation & Dual-Signature Access

**Core failure modes:** Budget Overdraft · Silent Exceedance · Authority Bypass · Missing Dual-Signoff · Single-Signature Assumption

---

## Your Input File
```
../data/budget/ward_projects.csv
```
Contains 7 municipal project funding proposals across 5 wards with requested budget allocations and approver IDs.

## Your Output File
```
uc-0d/allocated_projects.csv
```

## Run Command
```bash
python app.py --input ../data/budget/ward_projects.csv --output allocated_projects.csv
```

---

## Business & Governance Rules — Your Enforcement Must Reference These Exactly

| Rule ID | Constraint | Enforcement Specification |
|---|---|---|
| **RULE-01** | **Threshold Gating** | Projects with `requested_amount_inr` > 100,000 INR **MUST** have approvals from **BOTH** Ward Officer (`AUTH-WARD-01`) AND Finance Controller (`AUTH-FIN-01`). |
| **RULE-02** | **Single Sign-off Limit** | Projects <= 100,000 INR require only 1 valid municipal official sign-off. |
| **RULE-03** | **Budget Overdraft Prevention** | The total allocated amount in any ward cannot exceed the ward's available balance (`Ward-1: 15M`, `Ward-2: 8.5M`, `Ward-3: 22M`, `Ward-4: 4.2M`, `Ward-5: 11M`). |
| **RULE-04** | **Rejection Audit Trail** | Any project failing signature or budget constraints must be marked `REJECTED` with an exact failure code (`INSUFFICIENT_SIGNATURES`, `EXCEEDS_WARD_BALANCE`). |

---

## Skills to Define in `skills.md`
- `get_ward_balance(ward_id: str)` — Retrieves real-time remaining ward balance.
- `verify_signoff(approver_ids: list, amount: float)` — Checks dual-signature validity for the requested amount.
- `commit_expenditure(project_id: str, ward_id: str, amount: float)` — Deducts amount from ward balance and logs transaction.

---

## What Will Fail From the Naive Prompt
Run `"Approve and allocate funds for these civic projects."` first.
Then look for:
1. `PRJ-2026-003` (1.2M INR) approved with only Ward Officer sign-off (missing Finance Controller).
2. `PRJ-2026-004` (350k INR) approved with only Finance Controller sign-off (missing Ward Officer).
3. `PRJ-2026-006` (5M INR) in Ward-4 approved despite Ward-4 only having 4.2M INR available (Overdraft).
4. Unclear or blank rejection reasons instead of strict audit codes.

---

## Commit Formula
```
UC-0D Fix [failure mode]: [why it failed] → [what you changed]
```
