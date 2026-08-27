# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes their numbered sections by document name and section number.
    input: A list of policy file paths or the policy directory.
    output: A structured document index containing section numbers, text, and source filenames.
    error_handling: If a document is missing or unreadable, return an explicit error and stop processing.

  - name: answer_question
    description: Finds the most relevant single-source policy section for a user question and returns a compliant answer or the required refusal template.
    input: A question string and the document index.
    output: A response string containing either the relevant policy text plus citation, or the exact refusal template.
    error_handling: If no strong match exists, return the refusal template exactly; if multiple documents appear relevant, refuse rather than blend them.
