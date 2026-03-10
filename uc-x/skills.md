# skills.md

skills:
  - name: retrieve_documents
    description: Opens and loads the three specified policy text files, indexing their contents logically by document name and explicit section numbers for exact citation.
    input: List of strings containing file paths to the HR, IT, and Finance policy documents.
    output: Dictionary mapping document names to their respective numbered section clauses and text.
    error_handling: Raise a system exception if any of the three required policy documents are missing or unreadable.

  - name: answer_question
    description: Analyzes the employee question against the indexed documents. It searches for a single, definitive matching clause that answers the question.
    input: A string representing the employee query, and the indexed dictionary output by `retrieve_documents`.
    output: A string containing the definitive answer with the required `[Document Name, Section Number]` citation, OR the exact refusal template.
    error_handling: Use the refusal template verbatim if no single clear answer exists, or if synthesizing an answer would require blending conditions from two different documents.
