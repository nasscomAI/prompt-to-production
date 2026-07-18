# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and clause/section number.
    input: None (reads fixed file paths for the 3 policy documents).
    output: A dict of {doc_name: {clause_number: clause_text}}.
    error_handling: If a document file is missing, prints a warning and continues indexing the remaining documents rather than crashing.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source cited answer, or the exact refusal template.
    input: index (from retrieve_documents), question (str).
    output: A string — either "Source: <doc>\n  Section <n>: <text>" or the refusal template verbatim.
    error_handling: If the best matches are weak or ambiguous (low keyword overlap, or top matches split evenly across two documents), returns the refusal template rather than guessing or blending.