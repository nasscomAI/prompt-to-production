skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for precise citation mapping.
    input: List of paths to policy documents (strings).
    output: A structured index mapping document names and section numbers to clauses (dictionary).
    error_handling: Exits completely and reports an error if a policy document fails to load.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer or triggers a strict refusal template.
    input: User's question string and the indexed documents mapping.
    output: A strictly compliant answer citing the source document and section, or the exact verbatim refusal template.
    error_handling: Unambiguously trips the verbatim refusal template upon detecting any ambiguity or out-of-bounds cross-document overlap.
