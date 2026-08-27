skills:
  - name: retrieve_documents
    description: Load and index the three policy text files by document name and section number.
    input: Three plain-text policy file paths.
    output: Searchable index keyed by document name, section number, and section text.
    error_handling: If any required file is missing or cannot be parsed into numbered sections, stop and report the specific file issue.

  - name: answer_question
    description: Match a user question to one policy document and return a cited answer or the refusal template.
    input: User question string plus indexed policy documents.
    output: Either a single-source answer with citations or the exact refusal template.
    error_handling: If the best evidence spans multiple documents, is ambiguous, or is unsupported, return the exact refusal template instead of blending or hedging.
