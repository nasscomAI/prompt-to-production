skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None (loads predefined files - policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt from ../data/policy-documents/)
    output: Indexed document structure containing document name, section number, and section content for all three policy files.
    error_handling: If any policy file is missing or unreadable, return an error message indicating which file could not be loaded. If a file lacks section numbers, index by paragraph or return the full document with a warning.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the refusal template if the question is not covered.
    input: String (user question about company policy) and indexed documents from retrieve_documents.
    output: String containing either (1) an answer derived from a single document with citation in format "[document_name, section X.X]" OR (2) the exact refusal template "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: If the question matches content in multiple documents, answer from the most specific single source only - never blend. If the question is ambiguous or could lead to cross-document blending, return the refusal template. If the question contains no policy-related content, return the refusal template. Never use hedging phrases or qualifiers.
