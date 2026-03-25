# skills.md

skills:
  - name: retrieve_documents
    description: Loads all provided policy files and indexes them by document name and section number.
    input: A list of strings representing file paths to policy documents.
    output: A JSON object containing the indexed text mapped by document name and section number.
    error_handling: Raise an error if any of the specified document files cannot be found or read.

  - name: answer_question
    description: Searches the indexed documents to return a single-source answer with a citation, or returns the strict refusal template if the answer is missing or requires cross-document blending.
    input: A string containing the user's question, and the indexed policy documents.
    output: A string containing the precise answer with a citation (document name + section), OR the exact refusal template.
    error_handling: If the answer cannot be confidently sourced from a single policy document section, instantly default to the refusal template.
