skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of policy document file paths.
    output: Indexed documents mapped by document name and section number.
    error_handling: If a file is missing or unreadable, halt execution and report the missing file.

  - name: answer_question
    description: Searches indexed documents to return a single-source answer with citation OR the refusal template.
    input: The user's question string and the indexed documents.
    output: A single-source answer string with citation, or the exact refusal template string.
    error_handling: If the question requires combining claims from multiple documents, or is not found in any document, return the exact refusal template with no variations.
