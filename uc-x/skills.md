# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: Directory path containing the policy .txt files.
    output: Dictionary mapping (doc_name, section_num) to section text.
    error_handling: Returns empty dict and logs error if files not found.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: question (string), indexed_documents (dict from retrieve_documents).
    output: Dictionary with keys: answer (string), source_doc (string), section_num (string), or refusal_template if not found.
    error_handling: If answer requires blending two sources, returns refusal template.
