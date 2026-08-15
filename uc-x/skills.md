# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: None. Hard-coded paths to the three policy files:
      ../data/policy-documents/policy_hr_leave.txt
      ../data/policy-documents/policy_it_acceptable_use.txt
      ../data/policy-documents/policy_finance_reimbursement.txt
    output: An in-memory index mapping document name + section number to the exact policy text for each of the three files.
    error_handling: If any policy file is missing or unreadable, do not guess the contents — report the missing file and refuse to answer until it is restored.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the refusal template verbatim.
    input: A plain-text employee question string.
    output: One of two forms — (1) a factual answer drawn from ONE document, citing document name + section number with all conditions stated exactly as written; (2) the refusal template verbatim:
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: Never combine claims from two different documents. If the question is not covered, or answering from a single source is ambiguous, return the refusal template. Never use hedging phrases ("while not explicitly covered", "typically", "generally understood", "it is common practice").
