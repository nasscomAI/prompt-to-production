skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number
    input: list of str - paths to policy files
    output: dict - keyed by document name with sections as {section_number: content}
    error_handling: If file not found, raise FileNotFoundError with clear message

  - name: answer_question
    description: Searches indexed documents, returns single-source answer with citation OR refusal template
    input: dict of indexed documents, str question
    output: str - answer with section citation OR refusal template
    error_handling: If no match found, return refusal template exactly; never combine two sources