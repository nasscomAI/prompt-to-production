# UC-X Testing Files

## Input Files (from data/policy-documents/)
- `policy_hr_leave.txt` — HR Leave Policy document
- `policy_it_acceptable_use.txt` — IT Acceptable Use Policy document
- `policy_finance_reimbursement.txt` — Finance Reimbursement Policy document

## Test Questions and Expected Answers

| # | Question | Expected Source | Expected Answer |
|---|----------|----------------|-----------------|
| 1 | Can I carry forward unused annual leave? | HR policy section 2.6 | Carry forward limited to 5 days, above 5 forfeited on 31 Dec |
| 2 | Can I install Slack on my work laptop? | IT policy section 2.3 | Requires written approval from IT Department |
| 3 | What is the home office equipment allowance? | Finance section 3.1 | Rs 8,000 one-time, permanent WFH only |
| 4 | Can I use my personal phone for work files from home? | IT policy section 3.1 | Personal devices may access CMC email and employee self-service portal only |
| 5 | What is the company view on flexible working culture? | Refusal template | Not covered in any policy document |
| 6 | Can I claim DA and meal receipts on the same day? | Finance section 2.6 | Cannot be claimed simultaneously for the same day |
| 7 | Who approves leave without pay? | HR section 5.2 | Department Head AND HR Director, both required |

## Run Command
```bash
python app.py --question "Can I carry forward unused annual leave?"
```

## Verification
- Single-source answers only — never blend HR+IT policies
- Refusal template used exactly when question not in documents
- No hedging phrases ("while not explicitly covered", "typically", etc.)
- Every factual claim cites document name + section number
