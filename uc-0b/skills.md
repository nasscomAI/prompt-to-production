# skills.md — UC-0B Policy Summarization Skills

skills:
  - name: retrieve_policy
    description: Load a plain text policy file and parse it into numbered sections with clause mappings.
    input: File path to policy .txt file with numbered sections (e.g., 2.3, 5.2) and clause-level text.
    output: Structured dictionary with keys {section_number, title, content, clause_reference}. All clauses numbered and mappable.
    error_handling: If file cannot be read, raise error with filename. If sections are malformed (missing numbers), log warning and include raw section in output.

  - name: summarize_policy
    description: Extract 10 key clauses from retrieved policy structure and produce binding-preserving summary with all conditions intact.
    input: Structured policy dict from retrieve_policy with all numbered clauses.
    output: Text file with summary format: "Clause [ref]: [obligation] → [binding verb] [condition(s)]". Every clause present. Multi-conditions preserved verbatim or with [QUOTED] marker.
    error_handling: If a clause is missing from source, document as [NOT PRESENT]. If a clause has >30 words or complex conditions, preserve verbatim with [QUOTED] marker instead of summarizing.
