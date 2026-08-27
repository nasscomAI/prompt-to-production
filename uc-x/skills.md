skills:
  - name: retrieve_documents
    description: Loads all 3 required policy files and structurally indexes them by document name and section number for precise citation.
    input: List of file paths to the three `.txt` policy documents.
    output: Indexed database dictionary mapping sections and filenames to raw text.
    error_handling: Exits if any of the three required documents are missing.

  - name: answer_question
    description: Searches the indexed documents to return a single-source answer with verbatim citations, OR returns the refusal template if the answer cannot be cleanly single-sourced without blending.
    input: User query string and the indexed documents database.
    output: Formatted answer string containing the section citation, OR the exact refusal template.
    error_handling: Defaults to the refusal template if no matching section is definitively found.
