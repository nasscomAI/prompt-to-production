skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of file paths to policy documents.
    output: A structured dictionary of indexed document sections.
    error_handling: Exits or reports an error if any of the required documents cannot be found or read.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation or the exact refusal template.
    input: A user question string and the indexed document dictionary.
    output: A formatted string containing the answer and citation, or the exact refusal template.
    error_handling: Always falls back to the exact refusal template if there is any ambiguity or if the question spans multiple documents without a unified source.
