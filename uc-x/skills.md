# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: Directory path containing the corporate policy .txt files.
    output: List of dictionaries representing the indexed sections and their content.
    error_handling: If a file is missing, log a warning but proceed with the available files.

  - name: answer_question
    description: Searches indexed documents and returns a strict, single-source answer with citation, or the refusal template.
    input: The parsed user query and the indexed document map.
    output: String containing the specific answer or the strict refusal message.
    error_handling: If results span multiple documents, discard the blended answer and return the strict refusal template immediately.
