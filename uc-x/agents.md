# Document Q&A Agents

- `PolicyQA_Agent`: A strict knowledge-retrieval agent. It is designed to provide answers to employee queries using only the provided policy documents as a source of truth. It adheres to a strict "no-blend" policy where information from multiple documents cannot be combined to form a new, unsourced conclusion.
- `RefusalGuard`: Ensures that any query not explicitly answered within a single document section is met with the standard refusal template.

## Refusal Template
This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.
