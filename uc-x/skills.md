# skills.md — UC-X Skills

skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and indexes the content by document filename and numbered section/clause.
    input: List of paths to policy text files (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`).
    output: Structured index mapping (doc_name, section_number) to clause text and search metadata.
    error_handling: If any required document file is missing or unreadable, raise a FileNotFoundError specifying which document failed to load.

  - name: answer_question
    description: Analyzes user query against the indexed documents, identifying the single authoritative source document and returning a direct answer with citation, or the refusal template.
    input: User question string and indexed documents mapping.
    output: String response containing either single-source answer with document and section citation, or the exact refusal template.
    error_handling: If no document covers the topic or if answering would require speculative cross-document blending, return the mandatory refusal template without hedging.

