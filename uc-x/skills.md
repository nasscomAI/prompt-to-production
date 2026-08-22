skills:
  - name: retrieve_documents
    description: Reads and indexes all policy files from the target directory, returning structured text indexed by document filename.
    input: Path string to the policy directory containing .txt files.
    output: A dictionary mapping filename keys to full text document contents.
    error_handling: If any file fails to load or directory is missing, log the error and terminate execution gracefully.

  - name: answer_question
    description: Processes user query against indexed policy files to return a single-source answer with section citations or the mandatory refusal template.
    input: A string user query and the indexed document dictionary.
    output: A string response containing single-source factual answer + citations OR exact refusal template.
    error_handling: If API call fails or input is malformed, return the default refusal template safely.