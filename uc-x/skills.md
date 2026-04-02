skills:
  - name: retrieve_documents
    description: Selectively loads and parses all three policy files (HR, IT, Finance) by segmenting their structural boundaries into query-able indices based on document name and section number.
    input: Directory path pointing to the array of original policy `.txt` files.
    output: A rigid knowledge base mapped purely by distinct source name and numbered section IDs.
    error_handling: Immediately limits the search index array if a file is missing rather than hallucinating external rules.

  - name: answer_question
    description: Performs a confined semantic search across the retrieved knowledge base to locate a single-source match, returning a cited answer or forcing the refusal block.
    input: A string query or question provided by the user.
    output: An explicit answer paired dynamically with the exact source document name and section number, OR the verbatim fallback refusal template.
    error_handling: Systematically blocks any response generation that draws from more than one document natively, returning the standard refusal template instead.
