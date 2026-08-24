# skills.md

skills:
  - name: retrieve_policy
    description: >
      Deterministic, non-AI parser. Splits a raw policy .txt file into an
      ordered list of numbered clauses. No summarization or rewriting —
      pure structural transform. A clause boundary is any line starting
      with an `<n>.<n>` marker (e.g. "2.3"); everything up to the next
      marker belongs to that clause.
    input: >
      File path or raw text of a plaintext policy document containing
      `<n>.<n>`-numbered clause headers in ascending order.
    output: >
      Ordered list of records — clause_number, section_heading, text —
      one per detected clause, in source order. Text is verbatim from
      the source; nothing summarized or dropped.
    error_handling: >
      Unreadable, missing, or empty file — raise, never return a partial
      structure. A stray number that doesn't match `<n>.<n>` is appended
      to the current clause's text, not treated as a new boundary. No
      recognizable clause markers at all — raise, rather than silently
      returning the whole file as one unnumbered clause, since
      enforcement depends on clause numbers existing.

  - name: summarize_policy
    description: >
      The only LLM-calling skill. Takes retrieve_policy's clause list and
      produces a compressed summary that preserves every clause's
      obligations, conditions, and binding force, using system_prompt.md
      to enforce agents.md's rules at generation time.
    input: >
      The full ordered clause list from retrieve_policy — not a subset,
      since cross-clause completeness and scope-bleed detection both
      need every clause in context.
    output: >
      One text document, one entry per input clause in clause order,
      each labeled with its clause number, containing either a
      compressed statement (preserving verb strength and all conditions)
      or a verbatim quote flagged "[VERBATIM — not summarized]". Output
      clause count must equal input clause count.
    error_handling: >
      Input missing clause_number fields, or empty — reject; this skill
      does not summarize unstructured text. After generation, verify
      every input clause_number appears in the output; if any is
      missing, treat it as a failed generation and surface the missing
      numbers rather than returning a silently incomplete summary. Any
      output statement that can't be traced to a source clause is
      dropped and flagged as unresolved rather than passed through.
