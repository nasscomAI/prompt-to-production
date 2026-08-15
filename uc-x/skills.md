# skills.md — UC-X Policy Document Q&A

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes them by document name and section number (e.g. "policy_it_acceptable_use.txt" -> {"3.1": {title, text}}).
    input: policy_dir (str) — directory containing the three policy files
    output: dict — {doc_name: {section_number: {title, text}}}
    error_handling: Missing policy files exit with a clear error naming the missing path.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source cited answer (document name + section number) or the exact refusal template.
    input: index (dict), question (str)
    output: str — answer with source citation, or the verbatim refusal template
    error_handling: Empty questions ask for a question; out-of-scope topics ("flexible working", "company culture") and questions matching no section return the refusal template exactly; the single-source rule prevents blending across documents.