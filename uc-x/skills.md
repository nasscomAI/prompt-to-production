# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes content by document name and section number for targeted retrieval.
    input: Directory path containing the three policy files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: A dictionary mapping document names to their indexed sections. Each section is stored with its section number, full text, and document source name.
    error_handling: If any of the three policy files are missing, raises FileNotFoundError listing which files were not found. If a file has no recognisable numbered sections, stores the full content under section "FULL" and logs a warning that section-level retrieval is not available for that document.

  - name: answer_question
    description: Searches indexed documents for a single-source answer to the user's question, returns the answer with citation or the refusal template.
    input: A question string and the indexed documents dictionary from retrieve_documents.
    output: A string containing either the factual answer with source document and section citation, or the exact refusal template if no document covers the question.
    error_handling: If the question is empty or whitespace-only, returns "Please provide a specific question." If the indexed documents dictionary is empty, raises ValueError. If the question matches content in multiple documents, selects the single most relevant document and answers from that source only — never blends.
