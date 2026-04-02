# skills.md

skills:
  - name: retrieve_documents
    description: Ingests the 3 target policy files into an isolated index keyed by Document Name and Section Number.
    input: List of 3 strings containing file paths.
    output: Internal knowledge graph mapping.
    error_handling: Halts if any of the three files fail to load.

  - name: answer_question
    description: Parses the employee's string query and searches for a definitive single-source match to formulate an answer.
    input: Employee query string.
    output: The extracted answer + clause citation, OR the exact refusal template.
    error_handling: Automatically routes to the refusal template if the query triggers results spanning multiple documents simultaneously, or triggers 0 documents.
