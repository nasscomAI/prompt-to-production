# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: Directory or list of paths to the three .txt policy files.
    output: A dict keyed by document name, each value a dict of section_number -> clause text.
    error_handling: >
      Raises a clear error if any of the three files is missing. Logs which documents
      loaded successfully so the answerer never cites an unloaded document.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the refusal template.
    input: The indexed documents dict and a free-text question string.
    output: A string: either a single-source answer citing "doc — section X.Y", or the exact refusal template.
    error_handling: >
      If no document contains the answer, returns the refusal template verbatim. If the
      best match would require blending two documents, refuses rather than blending.
      Never returns a hedged or invented answer.
