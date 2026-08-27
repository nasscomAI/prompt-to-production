skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of file paths to the policy documents.
    output: Indexed text content structured by document name and section number.
    error_handling: Returns an error if any of the specified policy files are missing or unreadable.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the refusal template.
    input: User's question as a string and the indexed document content.
    output: A string containing either the single-source answer with document and section citation, or the exact refusal template.
    error_handling: Returns the exact refusal template if the question is not in the documents or if answering would require blending claims from two different documents.
