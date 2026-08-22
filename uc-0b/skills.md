# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into structured, numbered sections and clauses.
    input: >
      A file path (string) to a UTF-8 encoded .txt policy document, e.g.
      ../data/policy-documents/policy_hr_leave.txt.
    output: >
      A structured object: an ordered list of sections, each with its section
      number, section title, and a list of clauses. Each clause carries its
      clause number (e.g. "5.2") and the exact clause text. No text is dropped,
      reordered, or paraphrased at this stage.
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error and stop
      (do not fabricate content). If a line cannot be matched to a clause number,
      retain it verbatim attached to the nearest preceding clause rather than
      discarding it.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant, clause-referenced summary that preserves every clause, condition, and binding verb.
    input: >
      The structured section/clause object produced by retrieve_policy.
    output: >
      A plain-text summary in which every numbered clause is represented and
      tagged with its clause number, all binding verbs (must / will / requires /
      not permitted) are preserved at original strength, and all conditions of
      multi-condition obligations are retained. Clauses that cannot be compressed
      without meaning loss are quoted verbatim and flagged.
    error_handling: >
      If a clause cannot be summarised without dropping a condition or softening
      an obligation, emit the clause verbatim with a
      [VERBATIM — could not compress without meaning loss] flag. Never add facts
      absent from the input and never omit a clause; if the input is empty or
      malformed, raise an error rather than producing a partial summary.
