# skills.md

skills:
  - name: retrieve_documents
    description: Loads HR, IT, and Finance policy files and indexes them by document name and section number.
    input: List of file paths to the policy documents.
    output: A structured index or searchable knowledge base of policy sections.
    error_handling: Raise an exception if any required document is missing or corrupted.

  - name: answer_question
    description: Searches the indexed documents for a specific answer. Returns a single-source response with citations or the refusal template if no match is found.
    input: User question (string) and the indexed knowledge base.
    output: String containing the specific answer + citation OR the refusal template.
    error_handling: If multiple documents contain conflicting information, prioritize the IT policy for device-related queries or HR for leave queries, but never blend.
