# skills.md — UC-X Skills

skills:
  - name: retrieve_documents
    description: Loads and indexes policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt by document name and section number.
    input: Base directory path to policy documents.
    output: A dictionary of indexed documents and numbered sections with exact text.
    error_handling: Handles missing policy files safely; ensures complete text indexing.

  - name: answer_question
    description: Matches citizen/employee policy questions to indexed sections, producing a single-source factual answer with citations or an exact refusal.
    input: Question string.
    output: A single-source answer with document name and section number citation, or the exact refusal template.
    error_handling: Strictly refuses without hedging when question is out of scope or requires unsafe cross-document blending.
