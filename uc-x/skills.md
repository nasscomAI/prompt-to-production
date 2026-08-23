# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: List of file paths to policy text files (strings).
    output: Structured in-memory index mapping document name → section number → section content (dict).
    error_handling: If a file is missing or unreadable, log the error and continue with the remaining available files.

  - name: answer_question
    description: Searches the indexed policy documents for a relevant section and returns a single-source answer with citation, or the refusal template.
    input: A user question string.
    output: Answer string with source document name and section number, OR the refusal template string if not covered.
    error_handling: If input is empty or no matching section is found in any document, return the refusal template with no elaboration.
