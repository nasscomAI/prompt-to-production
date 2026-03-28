skills:
  - name: retrieve_documents
    description: Loads the three policy files and builds a section-indexed lookup by document name and section number.
    input: "Array of file paths: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt."
    output: "Structured index {documents:[{name, sections:[{section_id, text}]}], section_lookup:map} for source-grounded question answering."
    error_handling: "If any file is missing or unreadable, return a blocking error with missing file names and do not answer questions from partial context. If section parsing is incomplete, return flag: NEEDS_REVIEW with parse warnings."

  - name: answer_question
    description: Answers a user policy question using exactly one document source and section citation, or returns the refusal template verbatim.
    input: "User question string plus structured document index from retrieve_documents."
    output: "Either (a) single-source answer with citation format 'source: <document_name> section <section_id>' or (b) exact refusal template text when not covered."
    error_handling: "If evidence is absent, ambiguous, or would require combining claims across documents, return exactly: 'This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance.' Never use hedging phrases or inferred policy statements."
