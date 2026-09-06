skills:
  - name: retrieve_policy
    description: Loads the HR policy text file and returns its content as structured numbered sections.
    input:
      type: file path
      format: .txt policy document
    output:
      type: structured sections
      format: numbered clauses with their original text
    error_handling: >
      If the file is missing, unreadable, or contains no numbered clauses,
      return an error and do not guess or invent policy content.

  - name: summarize_policy
    description: Produces a compliant summary of structured policy sections with clause references.
    input:
      type: structured sections
      format: numbered clauses and original policy text
    output:
      type: text summary
      format: summary containing clause references and preserved obligations
    error_handling: >
      Preserve every clause and all conditions. Do not add information outside
      the source document. If a clause cannot be summarized without meaning
      loss, quote it verbatim and flag it.