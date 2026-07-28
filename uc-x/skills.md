skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files from ../data/policy-documents/, parses
      each file into sections by heading/number, and returns an index keyed
      by document name and section number.
    input: >
      None (operates on a fixed set of file paths).
    output: |
      A dict of shape:
        { "<filename>": { "<section_number>": "<section_text>", ... }, ... }
    error_handling: >
      If a file is missing or unreadable, raise FileNotFoundError with the
      missing file path. Do not proceed with a partial index.

  - name: answer_question
    description: >
      Searches the indexed documents for the user's question, returns a
      single-source answer with a document name + section citation, or
      returns the verbatim refusal template if no match is found.
    input: |
      A question string (str) and a document index (dict from
      retrieve_documents).
    output: |
      A string — either the refusal template or an answer of the form:
        "According to <document_name> (section <X.Y>): <answer>"
    error_handling: >
      If input index is empty or invalid, return the refusal template.
      Never blend two sections or two documents.
