skills:
  - name: retrieve_documents
    description: Loads all available policy files and creates a searchable index based on document names and section numbers.
    input: A list of file paths to policy documents.
    output: An indexed knowledge base of policy clauses and sections.
    error_handling: Reports any documents that failed to load or parse correctly.

  - name: answer_question
    description: Searches the indexed documents for an answer to a user query and returns a cited response or a formal refusal.
    input: A user question string.
    output: An answer with citations (doc name + section) OR the mandatory refusal template.
    error_handling: If multiple documents provide conflicting or ambiguous information, the agent must refuse and point to the relevant teams for clarity.
