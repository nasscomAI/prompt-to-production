skills:
  - name: retrieve_documents
    description: Loads all three CMC policy files and indexes them by document name and section number.
    input: policy_dir (string) - Path to the directory containing the three policy text files.
    output: index (dictionary mapping document name to a list of sections, each containing section number and text).
    error_handling: If any of the three required policy files is missing or unreadable, prints an error to stderr and exits non-zero.

  - name: answer_question
    description: Searches the indexed policy documents for a single-source answer to a question and returns it with a citation, or returns the exact refusal template if not found.
    input: question (string), index (dictionary from retrieve_documents).
    output: answer (string) - Single-source policy answer with citation (document name + section number), or the exact refusal template.
    error_handling: If the question could be answered from multiple documents simultaneously (cross-doc blending risk), always return the single most relevant source only, or use the refusal template.
