skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its contents as structured numbered sections.
    input:
      type: file_path
      format: Path to a readable .txt policy document.
    output:
      type: structured_sections
      format: Ordered list of numbered clause references and their exact source text.
    error_handling:
      - Reject missing, unreadable, or non-.txt input files with a clear error.
      - Reject documents whose numbered clauses cannot be parsed unambiguously and request a valid source document.
      - Preserve source text exactly; do not infer, omit, soften, or add policy content.
  - name: summarize_policy
    description: Produces a compliant policy summary from structured numbered sections while retaining clause references and all binding conditions.
    input:
      type: structured_sections
      format: Ordered numbered clause references with exact source text.
    output:
      type: text
      format: Summary containing clause references and a complete representation of every numbered source clause.
    error_handling:
      - Reject invalid, empty, or ambiguously structured sections with a clear error.
      - Validate that every numbered clause is represented before returning output.
      - Preserve every condition in multi-condition obligations, including all required approvers, deadlines, exceptions, and consequences.
      - Reject or remove unsupported additions and scope-bleed language not present in the source.
      - If a clause cannot be summarized without meaning loss, quote it verbatim and flag it.