# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered
      sections and clauses, keeping every clause's exact wording.
    input: >
      Path to a policy document (.txt), e.g. ../data/policy-documents/policy_hr_leave.txt.
    output: >
      An ordered list of clauses keyed by their number (e.g. 2.3, 2.4, 5.2) with
      the verbatim source text of each clause.
    error_handling: >
      Raises an error if the file is missing or empty. Clauses that cannot be parsed
      as numbered sections are preserved verbatim and flagged rather than dropped.

  - name: summarize_policy
    description: >
      Produces a faithful summary from the structured clauses, preserving every
      numbered clause, every binding verb, and every condition attached to it.
    input: >
      The structured clause list from retrieve_policy.
    output: >
      Writes uc-0b/summary_hr_leave.txt containing one entry per numbered clause
      with its exact obligation. Multi-condition obligations keep ALL conditions —
      e.g. clause 5.2 names both Department Head and HR Director.
    error_handling: >
      Never omits a clause, never adds information not in the source, and never
      softens a binding verb. If a clause cannot be preserved without meaning loss
      it is quoted verbatim and flagged instead of paraphrased.
