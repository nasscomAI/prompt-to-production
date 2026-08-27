# skills.md — UC-X

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None — loads from predefined paths
    output: dict — keys are document names, values are dicts of section_number: section_text
    error_handling: If any file is missing, prints warning and skips it. Returns partial index.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer with citation or refusal template.
    input: str — user question
    output: str — answer with source citation, or refusal template
    error_handling: If question is empty, returns refusal template. If multiple sources match, returns refusal to avoid blending.
