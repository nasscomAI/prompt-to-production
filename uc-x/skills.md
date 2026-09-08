skills:
  - name: retrieve_documents
    description: Loads and indexes all policy files from data/policy-documents/ into structured, searchable section and clause nodes keyed by document name and section number.
    input: List of filepaths to policy text documents (e.g., policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Indexed database of structured document nodes with document reference, section number, title, and full clause text.
    error_handling: Raises FileNotFoundError if any policy document is missing; logs a warning and validates section header structure.

  - name: answer_question
    description: Queries the indexed policy database to find the single most relevant document section, validates single-source attribution, and returns a cited answer or the exact refusal template.
    input: Question string from the user.
    output: Structured response containing the answered text, source document citation(s), section numbers, or the exact refusal template.
    error_handling: Detects cross-document contamination and strips cross-document blending; detects out-of-scope/uncovered questions and falls back to the exact refusal template without hedging.
