# skills.md
skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None required, or optionally the file paths to the policy documents (List of Strings).
    output: Indexed text content mapped by document name and section number (Dictionary/JSON).
    error_handling: If a file is missing or unreadable, throw an error citing the specific missing file name.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the exact refusal template.
    input: The user's question (String) and the indexed documents (Dictionary/JSON).
    output: A precise answer with document and section citation, or the exact refusal template (String).
    error_handling: If the answer requires combining information from multiple documents, or if the source is ambiguous, return the exact refusal template.
