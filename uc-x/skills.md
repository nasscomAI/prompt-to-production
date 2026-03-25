# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes the 3 policy files (HR, IT, Finance) by document name and section number for precise retrieval.
    input: File paths to policy documented in text format.
    output: A structured database or index map of policy clauses.
    error_handling: Reports an error if any of the three mandatory policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to provide a single-source answer with citations or returns the verbatim refusal template.
    input: String containing the employee's question.
    output: A precise response consisting of the answer, source file, section citation OR the mandatory refusal message.
    error_handling: Defaults to the refusal template if the answer involves cross-document ambiguity or is not explicitly stated.
