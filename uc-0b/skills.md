# skills.md

skills:
  - name: retrieve_policy
    description: >
      Load the supplied HR leave policy text and return its numbered clauses
      as structured sections for reliable downstream summarization.
    input: >
      A path to the policy_hr_leave.txt file.
    output: >
      Structured numbered policy sections containing clause references and
      their source text.
    error_handling: >
      If the file is missing, unreadable, or cannot be parsed into numbered
      sections, report the problem and do not invent or reconstruct missing
      policy content.

  - name: summarize_policy
    description: >
      Produce a clause-referenced HR leave policy summary that preserves all
      required obligations, conditions, approvals, limits, deadlines, and
      consequences from the structured policy sections.
    input: >
      Structured numbered sections extracted from policy_hr_leave.txt.
    output: >
      A concise text summary containing all required clause references and
      preserving every material condition from the source policy.
    error_handling: >
      If a clause cannot be summarized without meaning loss, preserve the
      relevant source wording and flag it for review rather than guessing or
      adding unsupported information.