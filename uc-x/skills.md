# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for fast lookup.
    input: >
      doc_dir (str): path to the directory containing policy documents.
    output: >
      A dict keyed by document filename, where each value is a dict of section_number → section_text.
      Example: {"policy_hr_leave.txt": {"2.3": "Employees must submit...", ...}, ...}
    error_handling: >
      If a file cannot be read, log a warning and continue with the remaining files.
      If no files can be read, raise an error.

  - name: answer_question
    description: Searches indexed documents for the answer, returns single-source answer with citation OR the refusal template.
    input: >
      question (str): the user's question.
      index (dict): the document index from retrieve_documents.
    output: >
      A string that is either:
      (a) An answer citing exactly one document + section number, OR
      (b) The exact refusal template if the question is not covered.
    error_handling: >
      If the question matches content in multiple documents, answer from the single
      most relevant document only. If blending would be required to answer, use the refusal template.
      Never produce a partial or hedged answer.
