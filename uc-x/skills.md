# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: A dict keyed by document name, each mapping section number (e.g. "3.1") to its full text.
    error_handling: If a file is missing or unreadable, raise a clear error rather than proceeding with partial documents.

  - name: answer_question
    description: Searches the indexed documents for a user question, returning a single-source answer with citation or the exact refusal template.
    input: A user question (string) and the indexed documents from retrieve_documents.
    output: Either an answer citing one document name + section number per claim, or the exact refusal template if the question is not covered by a single document or would require blending documents.
    error_handling: If matching content spans two documents such that only a blended (unstated) answer would result, use the refusal template rather than combining them.
