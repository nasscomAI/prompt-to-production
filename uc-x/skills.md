skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: List of 3 absolute or relative paths to the policy text files
    output: A nested dictionary structure organizing text by document and section number
    error_handling: System entirely halts if any of the three mandatory policy files are missing or unreadable.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: User's question string and the output of retrieve_documents
    output: A string containing the strict single-source answer and citation, or the verbatim refusal template
    error_handling: Checks for multi-document matches and strict refusal if the match is spanning multiple documents or missing entirely.
