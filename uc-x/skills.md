# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: List of document pathways (`list[str]`) or directory pathway (`str`).
    output: Indexed representation of the files organized by document name and section number (e.g. `dict` or structured objects).
    error_handling: Raise a clearly defined error if any of the three required policy documents are missing, unreadable, or missing section numbers.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: User's question (`str`) and the indexed documents object from `retrieve_documents`.
    output: Single-source answer string with exact citation (document name + section), or the exact verbatim refusal template.
    error_handling: Return the exact refusal template if the answer cannot be found in a single source, or if a multi-source combination creates genuine ambiguity. Never blend policies.
