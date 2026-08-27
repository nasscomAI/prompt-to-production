# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Parses a City Municipal Corporation policy document into discrete, indexable clauses.
    input:
      type: file_path
      format: .txt (Plain text with section headers and numbered sub-clauses)
    output:
      type: array
      items:
        clause_id: string (e.g., "2.3", "5.2")
        text: string (The full original content of the clause)
    error_handling: Detects and reports if the document reference or version is missing from the header.

  - name: summarize_policy
    description: Condenses policy clauses into accurate summaries while preserving all mandatory conditions and binding verbs.
    input:
      type: array
      items:
        clause_id: string
        text: string
    output:
      type: string
      format: Markdown (Clause-by-clause summary maintaining all 'must', 'will', and multi-party approval requirements)
    error_handling: If a clause contains more than 3 distinct conditions, the skill must flag it and include a verbatim 'Ground Truth' quote.
