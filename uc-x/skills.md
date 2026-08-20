# Skills

## retrieve_documents

Purpose:
Load and index all three policy documents separately.

Documents:
- policy_hr_leave.txt
- policy_it_acceptable_use.txt
- policy_finance_reimbursement.txt

Rules:
- Read all three documents.
- Keep each document separate.
- Index information by document name and section number.
- Do not combine claims from different documents.

## answer_question

Purpose:
Answer questions using the indexed policy documents.

Rules:
- Search the documents for the requested information.
- Answer using a single policy document only.
- Include the document name and section number for every factual claim.
- Never combine claims from different documents.
- Never guess or invent information.
- Never use hedging phrases such as "typically", "generally", "while not explicitly covered", or "it is common practice".
- If the question is not covered by the documents, use the exact refusal template.

Refusal template:

This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.