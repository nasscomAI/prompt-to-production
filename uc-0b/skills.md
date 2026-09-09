 skills:
  - name: retrieve_policy
    description: >
      Loads the provided HR leave policy text file and returns its contents
      as structured numbered sections so that every relevant clause can be
      identified and verified.

    input:
      type: text file
      format: >
        A .txt policy document containing numbered policy sections and clauses.

    output:
      type: structured sections
      format: >
        A structured representation containing the section and clause number,
        clause text, and all conditions, obligations, approval requirements,
        time limits, exceptions, and forfeiture rules stated in the source.

    error_handling: >
      If the policy file cannot be read or a clause cannot be identified
      reliably, report the issue rather than inventing or reconstructing
      missing policy content.

  - name: summarize_policy
    description: >
      Takes the structured policy sections and produces a clause-complete
      summary with explicit clause references while preserving the meaning
      and binding force of every requirement.

    input:
      type: structured policy sections
      format: >
        Numbered policy clauses returned by retrieve_policy.

    output:
      type: text summary
      format: >
        A concise but complete policy summary containing all ten ground-truth
        clauses with their clause references, obligations, conditions,
        approval authorities, deadlines, exceptions, and forfeiture rules.

    error_handling: >
      Never silently omit a numbered clause or condition. If a clause cannot
      be summarized without meaning loss, quote the relevant source text
      verbatim and flag it for review. Do not add external information,
      assumptions, interpretations, or standard practices.