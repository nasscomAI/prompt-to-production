# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a local .txt policy document and parses it into a structured format keyed by numbered sections and clauses to ensure indexing integrity.
    input:
      type: file_path
      value: "path to policy_*.txt"
    output:
      type: dict
      schema: { "clause_id": "clause_text" }
    error_handling: If file is missing or unreadable, return a failure status and do not proceed with summarization.

  - name: summarize_policy
    description: Transforms structured policy clauses into a condensed summary while enforcing 100% retention of binding conditions, specific approvers, and strict timelines.
    input:
      type: dict
      source: "output from retrieve_policy"
      requirements: "Must check specifically for clauses: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2."
    output:
      type: string
      format: "Markdown summary with explicit clause IDs for every obligation mentioned."
    error_handling: If a clause cannot be summarized without dropping a condition, the skill must return the verbatim text of that clause instead of a summary.
