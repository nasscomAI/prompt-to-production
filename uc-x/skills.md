# skills.md — UC-X Policy Document Q&A Agent

skills:
  - name: retrieve_documents
    description: Ingests all policy text files from the repository and indexes them hierarchically by document filename, section title, and numbered clauses.
    input: policy_dir (str, directory path containing policy .txt documents).
    output: Indexed dictionary mapping document names to structured section and clause collections.
    error_handling: Verifies presence of all 3 essential policy files (HR, IT, Finance); raises clear errors if required policy files are missing.

  - name: answer_question
    description: Evaluates a user question against indexed policy documents, matches relevant clauses from a single source document, and formats the response with precise citations or outputs the exact refusal template.
    input: question (str) and indexed_docs (dict).
    output: Dictionary containing answer (str), source_document (str), section_citation (str), and status (str: 'ANSWERED' or 'REFUSED').
    error_handling: Detects queries missing from documents and immediately triggers the exact refusal template; forbids cross-document synthesis or speculative answers.
