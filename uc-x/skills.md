# skills.md — UC-X Skills

skills:

retrieve_documents:
Loads the following files:
- policy_hr_leave.txt
- policy_it_acceptable_use.txt
- policy_finance_reimbursement.txt

Indexes them by:
document_name
section_number
policy_text


answer_question:

Process:
1. Search indexed documents for the question.
2. If an answer exists in ONE document:
   return the exact policy meaning with citation.

3. If the question requires combining two documents:
   refuse using the refusal template.

4. If the question is not present in any document:
   refuse using the refusal template.

Output:
Answer + citation OR refusal template.