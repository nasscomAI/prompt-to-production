# skills.md
skills:
  - name: retrieve_documents
    description: Loads and indexes all 3 policy documents by section number
    input: None (uses hardcoded file paths)
    output: Dict of {doc_name: {section_num: text}}
    error_handling: Raise FileNotFoundError if any policy file missing

  - name: answer_question
    description: Searches indexed documents, returns single-source answer with citation
    input: Question string
    output: Answer string with [Document, Section X.X] citation OR refusal template
    error_handling: Return refusal template if question not found in any document