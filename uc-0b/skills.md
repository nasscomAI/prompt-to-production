skills:
  - name: retrieve_policy_documents
    description: Loads company policy documents and organizes them for search.
    input: Path to the policy-documents directory containing text files.
    output: Dictionary mapping document names to lists of policy clauses or lines.
    error_handling: If a file cannot be read or is missing, skip the file and continue loading the remaining documents.

  - name: extract_policy_clause
    description: Searches the loaded policy documents to find the clause that answers a user's question.
    input: User question string and the dictionary of loaded policy documents.
    output: Exact policy clause text along with the source document name and line or section reference.
    error_handling: If no relevant clause is found in the documents, return a refusal response indicating the question is not covered in the available policy documents.