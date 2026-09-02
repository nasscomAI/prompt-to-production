# skills.md — UC-X Document Retrieval Skills

skills:
  - name: retrieve_documents
    description: Reads all 3 policy text files from data/policy-documents and indexes text sections by document name and section number.
    input: Path string pointing to the policy documents directory.
    output: Dictionary mapping document names to section numbers and text snippets.
    error_handling: Raises FileNotFoundError if any of the target policy text files are missing.

  - name: answer_question
    description: Performs target keyword search against indexed sections and returns a single-source attributed response or exact refusal template.
    input: Question string from user and indexed documents dictionary.
    output: Answer string with single-source citation or exact refusal output.
    error_handling: Returns exact refusal template when no relevant document section matches the question scope.