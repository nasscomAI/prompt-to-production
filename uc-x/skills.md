skills:
  - name: retrieve_documents
    description: Loads the three approved policy files and indexes content by document name and section number.
    input: "Array of file paths (string[]) for: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt."
    output: "Structured index object keyed by document name, then section number, with normalized section text and metadata."
    error_handling: "If any required file is missing, unreadable, or unparseable into sections, return a hard error with the failing file name and do not produce a partial index."

  - name: answer_question
    description: Answers a user policy question using one document source with section citations, or returns the exact refusal template.
    input: "Object with question (string) and indexed_documents (retrieve_documents output)."
    output: "Either (a) single-source answer text with citation for each factual claim in format 'document_name section X.Y', or (b) exact refusal template text."
    error_handling: "If the question cannot be answered from a single document, if coverage is missing, if citations are unavailable, or if ambiguity would require combining claims from multiple documents, return exactly: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
