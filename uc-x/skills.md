skills:
  - name: retrieve_documents
    description: Load all policy files (HR, IT, Finance) and index their content by document name and section number.
    input: List of paths to policy text files.
    output: An indexed knowledge base mapping document names and section numbers to text contents.
    error_handling: Raise an error if any of the target documents are missing or fail to parse.

  - name: answer_question
    description: Search the indexed documents for a specific user question, and return an answer derived from a single source document with citation, or return the refusal template.
    input: A string user question, and the indexed knowledge base.
    output: A string containing the answer with source citations (document name + section), or the exact refusal template if the information is missing or creates ambiguous cross-doc blending.
    error_handling: Reject questions that combine multiple documents in a conflicting or ambiguous way, returning the refusal template.
