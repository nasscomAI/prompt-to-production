# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three required policy files and indexes their content by document name and section number.
    input: None or list of file paths.
    output: A structured index or concatenated string of the documents mapped to their filenames and sections.
    error_handling: System exits gracefully with a warning if any of the three required policy documents are missing.

  - name: answer_question
    description: Searches the indexed documents to answer the user's question, applying the strict single-source rule and citations.
    input: The user's question (string) and the aggregated policy texts.
    output: The compliant, single-source text answer including citations, or the exact refusal template.
    error_handling: If the intent is unclear or no match is found, immediately output the strict refusal template.
