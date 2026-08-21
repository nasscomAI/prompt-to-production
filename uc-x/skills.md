# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to the policy documents (List of strings).
    output: A structured dictionary mapping document names and section titles to their specific content (Dictionary/JSON).
    error_handling: If a file is missing or unreadable, logs an error and skips the file, but alerts the user that a document couldn't be loaded.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation or the exact refusal template.
    input: The user's question (String) and the required refusal template (String).
    output: The extracted answer with source document and section citation, or the exact refusal template (String).
    error_handling: If the query matches multiple conflicting sources or cannot be mapped to a single source section, strictly returns the refusal template.
