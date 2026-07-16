# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section/clause number.
    input: A list of 3 file paths (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A dict {document_name: [{section_number, heading, clauses: [{clause_number, text}]}]} covering every clause in each document.
    error_handling: If any of the 3 files is missing/unreadable, raises a clear error rather than answering questions against a partial document set.

  - name: answer_question
    description: Searches the indexed documents for the question, and returns either a single-source answer with citation(s) or the fixed refusal template.
    input: query (free-text question string), index (from retrieve_documents).
    output: Either {"answer": text, "citations": [{"document": name, "section": number}, ...]} sourced from exactly one document, or {"refusal": REFUSAL_TEMPLATE} verbatim.
    error_handling: If no document has a relevant match, or if two-plus documents are only ambiguously/tied relevant with no single clear source, returns the refusal template rather than guessing or blending — never fabricates a citation.
