# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files, parses numbered sections, and indexes by document name + section number.
    input: List of file paths.
    output: Dict keyed by (document_name, section_number) with section text as value.
    error_handling: If a file is missing, report which one and continue with available files.

  - name: answer_question
    description: Searches indexed documents for relevant sections, returns single-source answer with citation OR exact refusal template.
    input: Question string, indexed documents dict.
    output: Answer string with citation OR refusal template string.
    error_handling: If multiple documents seem relevant, pick the most specific single source. If none match, use refusal template.