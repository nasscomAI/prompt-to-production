skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) pointing to a plain-text policy document.
    output: Structured content with each numbered clause preserved as a discrete section (clause number + full text).
    error_handling: If the file is missing or unreadable, return an error message and halt. If no numbered clauses are detected, return the raw text and flag that structure could not be parsed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all clause obligations, binding verbs, and multi-condition requirements with exact clause references.
    input: Structured numbered sections (output of retrieve_policy).
    output: Plain-text summary where every numbered clause is present, all conditions are intact (no silent drops), no information outside the source is added, and verbatim quotes are used for clauses that cannot be summarised without meaning loss.
    error_handling: If a clause contains a multi-condition obligation (e.g., requires two named approvers), include all conditions explicitly. If summarising a clause risks meaning loss, quote it verbatim and append a flag noting the direct quote.
