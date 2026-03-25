# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy files and indexes them by document name and section number for efficient searching.
    input: None (uses predefined file paths).
    output: A collection of indexed policy sections.
    error_handling: If any of the required policy files are missing, report which files are missing and continue with available ones.

  - name: answer_question
    description: Searches the indexed documents for a relevant answer and returns it with a citation or the refusal template.
    input: An employee's question as a string.
    output: A string containing the answer + citation OR the refusal template.
    error_handling: If multiple documents contain conflicting information, prioritize a single-source answer or refuse with the template.
