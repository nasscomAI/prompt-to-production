# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number for lookup.
    input: Paths to the three policy text files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A map from document name to its numbered sections and clauses (e.g. {"policy_it_acceptable_use.txt": {"3.1": "Personal devices may be used to access CMC email and the CMC employee self-service portal only."}}).
    error_handling: If any file is missing, unreadable, or contains no numbered clauses, return an explicit error listing the gap; do not proceed with a partial or fabricated index.

  - name: answer_question
    description: Searches the indexed documents for a question and returns a single-source answer with citation, or the refusal template verbatim.
    input: The indexed documents from retrieve_documents and a free-text question (string).
    output: An answer grounded in exactly one document, citing document name + section number, preserving all conditions; or the exact refusal template when the question is not covered or would require blending two documents.
    error_handling: If the question is not covered by any single document, or answering would require combining facts from two documents, return the refusal template verbatim rather than hedging or guessing.
