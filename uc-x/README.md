# UC-X — Ask My Documents

## Purpose
Answer questions using the three supplied CMC policy documents without blending claims across documents.

## Input documents
- `../data/policy-documents/policy_hr_leave.txt`
- `../data/policy-documents/policy_it_acceptable_use.txt`
- `../data/policy-documents/policy_finance_reimbursement.txt`

## Run

```bash
python app.py
```

If your working directory is different:

```bash
python app.py --data-dir ../data/policy-documents
```

## Output
Each supported answer includes the source document and section number. If no single document supports the answer, the program returns the exact refusal template required by this UC.

## Refusal template

```text
This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.
```

## Required tests

1. `Can I carry forward unused annual leave?`
2. `Can I install Slack on my work laptop?`
3. `What is the home office equipment allowance?`
4. `Can I use my personal phone for work files from home?`
5. `What is the company view on flexible working culture?`
6. `Can I claim DA and meal receipts on the same day?`
7. `Who approves leave without pay?`

The implementation must never invent permissions, blend HR/IT/Finance claims, or use hedged policy language.
