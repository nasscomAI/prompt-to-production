skills:
  - name: retrieve_documents
    description: Loads all corporate policy files and indexes text records by document name keys and section sub-headings.
    input: None. Scans predetermined target workspace path channels.
    output: Dict structure mapping document strings to section clause content objects.
    error_handling: Halts execution immediately via standard error codes if any system document is missing from the file target paths.

  - name: answer_question
    description: Verifies user questions against the indexed matrix, checking matching scopes and selecting single-source answers.
    input: Base knowledge dictionary paired with raw lower-case user search query strings.
    output: String payload containing exact text rules and explicit metadata citations, or the mandatory refusal message.
    error_handling: Automatically stops execution and returns the refusal block if a cross-document content blend risk is detected.