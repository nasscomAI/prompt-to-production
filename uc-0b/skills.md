# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and parses it into structured, numbered sections
      and clauses so nothing can be silently dropped downstream.
    input: >
      input_path (str) — path to a policy .txt file (e.g. policy_hr_leave.txt).
    output: >
      A structured object: an ordered list of sections, each with its heading and
      an ordered list of clauses, where each clause has its number (e.g. "5.2")
      and its full text. Also returns the complete set of clause numbers found.
    error_handling: >
      If the file cannot be opened, fail fast with a clear message. If a line
      cannot be attributed to a clause number it is attached to the most recent
      clause rather than discarded, so no source text is lost.

  - name: summarize_policy
    description: >
      Produces a clause-referenced summary from the structured sections,
      preserving every clause, every binding verb, and every condition.
    input: >
      The structured sections object returned by retrieve_policy.
    output: >
      A text summary string: one labelled entry per numbered clause (clause number
      + preserved obligation), multi-condition clauses tagged
      [MULTI-CONDITION PRESERVED], verbatim clauses tagged [VERBATIM], plus a
      verification footer listing every clause number covered vs. found in source.
    error_handling: >
      If a clause cannot be condensed without meaning loss, it is reproduced
      verbatim and flagged rather than reworded. If the covered clause set does
      not equal the source clause set, the summary emits an explicit
      COMPLETENESS WARNING naming the missing clause numbers.
