# skills.md — UC-X Multi-Document Policy QA

skills:
  - name: retrieve_documents
    description: Ingests all policy text files and indexes individual clauses by document filename and section identifier.
    input: file_paths (list of str) - paths to policy files
    output: dict mapping (doc_name, section_number) tuples to clause text
    error_handling: Silently skips missing files and returns indexed records for available files.

  - name: answer_question
    description: Answers a policy query using single-source attribution, ensuring no cross-document synthesis and zero hedging.
    input: question (str), indexed_docs (dict)
    output: formatted string with document and section citation, or exact refusal template
    error_handling: Emits the exact standardized refusal template if the query is out of scope or not directly documented.
