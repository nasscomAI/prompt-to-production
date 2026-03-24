# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 CMC policy files and indexes their content by document name and section number for single-source retrieval.
    input: None (automatically loads policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt from ../data/policy-documents/)
    output: Indexed document structure mapping document name → section number → section content. Each section retains its source document name and section identifier.
    error_handling: If any of the 3 required policy files cannot be loaded, return error specifying which file(s) are missing. Do not proceed with partial document set.

  - name: answer_question
    description: Searches indexed policy documents and returns a single-source answer with exact citation OR the refusal template if question is not in documents.
    input: String (user question about CMC policy)
    output: Either (1) single-source answer in format "According to [document_name] section X.Y, [fact]." OR (2) exact refusal template "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: |
      - If question matches content in multiple documents: answer from ONE source only OR use refusal template if ambiguity exists
      - If question is not directly addressed in any document: return refusal template verbatim
      - If question would require blending information across documents: use refusal template
      - Never use hedging phrases ("typically", "generally", "while not explicitly covered")
      - Never combine claims from different documents into a single answer
