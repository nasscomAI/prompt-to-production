# agents.md

## Enforcement Rules
1. Never combine claims from two different documents into a single answer (e.g. blend IT policies with HR tools allowances).
2. Never use hedging phrases: "while not explicitly covered", "typically", "generally understood", "it is common practice". Answers must be definitive facts or definitive refusals.
3. If question is not firmly and explicitly answered in the documents — use the refusal template EXACTLY, with no variations or surrounding text:
```
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.
```
4. Cite source document name + section number for every single factual claim provided. Outputs lacking citation must be aborted.
