# UC-X Skills

## retrieve_documents

Load all three policy documents:
- policy_hr_leave.txt
- policy_it_acceptable_use.txt
- policy_finance_reimbursement.txt

Index each document separately by:
- document name
- section number
- section content

Keep all sources separate.

## answer_question

Search the indexed documents and answer only when the question is supported by one document.

Rules:
1. Include the document name and section number for every factual claim.
2. Never combine claims from two documents in one answer.
3. Never invent unsupported information.
4. If the question is out of scope, use the exact refusal template from the agent instructions.
5. Do not use hedging phrases.
6. For the personal-phone/work-files question, use IT section 3.1 only or refuse.