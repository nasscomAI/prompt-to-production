skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files and indexes them by document name and section number.
    input: list of file paths (3 .txt files)
    output: dict mapping document_name → dict of section_number → section_text
    error_handling: if any file is missing, raise FileNotFoundError naming the missing file; partial load is not acceptable

  - name: answer_question
    description: Searches indexed documents for the best single-source answer to a question, returns answer with citation or refusal template.
    input: question (str), index (dict from retrieve_documents)
    output: str — either a direct answer ending with [Source: filename section X.X], or the exact refusal template if no document answers the question
    error_handling: if multiple documents match equally, prefer the most specific section and note the choice; never blend two documents