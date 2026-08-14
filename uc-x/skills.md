# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: An index mapping document name → section number → full section text, with no sections merged or lost.
    error_handling: If a file is missing or unreadable, reports the failure and refuses to answer questions until all three documents are loaded — it never answers from a partial index.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source cited answer or the refusal template.
    input: A free-text question and the document index from retrieve_documents.
    output: Either a factual answer citing the source document name and section number, or the exact refusal template (This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.).
    error_handling: If the question maps to claims in more than one document, it returns the answer from the single most specific document or refuses — it never blends. If no document covers the question, it returns the refusal template verbatim with no hedging.
