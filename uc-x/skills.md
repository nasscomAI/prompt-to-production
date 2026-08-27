# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy text files and parses/indexes them by document name and section number.
    input: Paths or directory containing the policy files.
    output: Data structure mapping document names and sections to their content.
    error_handling: Raise error if documents are missing or fail to read.

  - name: answer_question
    description: Searches the parsed sections for content relevant to the user query, and returns a single-source cited answer or the exact refusal template.
    input: Search query and indexed document structure.
    output: Cited text response or refusal response.
    error_handling: Fall back to the refusal template if the query does not match any indexed policies or is ambiguous.
