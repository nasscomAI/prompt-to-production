# skills.md — UC-0B Policy Summary Skills

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts content into structured, numbered sections.
    input: File path to the .txt policy document.
    output: A structured list or dictionary containing clause numbers and their full text content.
    error_handling: Return a fatal error if the file is missing, unreadable, or contains no detectable clause structure. Do not attempt to guess missing content.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant summary that preserves all obligations and multi-condition requirements.
    input: Structured policy sections (output from retrieve_policy).
    output: A refined summary focusing on core obligations, binding verbs, and specific conditions.
    error_handling:
      - Fail if any ground-truth clause (e.g., 5.2, 3.4) is missing from the summary.
      - If a multi-condition clause (like 5.2) has a condition dropped, reject the summary.
      - If the summary contains "scope bleed" (e.g., "standard practice"), return an error for non-compliance.
      - For complex clauses where meaning might be lost, the skill should revert to quoting the clause verbatim and flagging it.