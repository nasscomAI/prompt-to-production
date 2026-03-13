# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number so citations can be accurate.
    input: None directly; statically knows the 3 file paths in the data directory.
    output: A structured dictionary of the documents mapping sections to text.
    error_handling: System crash if any required document is missing.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer with a citation, or exact refusal template.
    input: User's question string.
    output: The exact answer string with citation, or the exact refusal template string.
    error_handling: Strict exact fallback to the refusal template if the answer is ambiguous, spans multiple documents, or is not found.
