skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexing them by document name and section number.
    input: Array of file paths (e.g., ["../data/policy-documents/policy_hr_leave.txt", ...]).
    output: An indexed dictionary mapping document names and section numbers to text content.
    error_handling: Logs an error and aborts if files are missing or unreadable.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the refusal template.
    input: The user's question (string) and the indexed documents mapping.
    output: A string containing the single-source answer with document name and section citation, or the exact refusal template.
    error_handling: Returns the exact refusal template if the answer cannot be found in a single source or if it would require cross-document blending.
