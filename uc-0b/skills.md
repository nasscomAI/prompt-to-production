# skills.md

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from the given path and returns its content
      as structured numbered sections, preserving all clause numbers and
      original wording verbatim.
    input: >
      File path (string) pointing to a .txt policy document.
      Example: "../data/policy-documents/policy_hr_leave.txt"
    output: >
      Ordered list of sections, each containing:
        - clause_id   (string, e.g. "2.3", "5.2")
        - heading     (string, section title if present, else empty)
        - body        (string, exact text of the clause, unmodified)
      Returns the full document structure so no clause is silently skipped.
    error_handling: >
      If the file path is invalid, the file is missing, or the file is empty,
      return an error object:
        { "error": "FILE_UNAVAILABLE", "message": "<reason>" }
      Do NOT attempt to summarise, infer content, or fall back to general
      knowledge. Propagate the error to the caller so the agent can trigger
      its refusal condition.

  - name: summarize_policy
    description: >
      Takes the structured sections produced by retrieve_policy and produces
      a clause-complete, obligation-faithful summary with explicit clause
      references, enforcing all rules defined in agents.md.
    input: >
      Ordered list of section objects (output of retrieve_policy):
        - clause_id   (string)
        - heading     (string)
        - body        (string)
    output: >
      Plain-text summary where:
        - Every clause appears with its clause_id cited (e.g. §2.3).
        - Binding verbs (must / will / requires / not permitted) are preserved
          exactly as they appear in the source body.
        - All conditions within a multi-condition clause are listed; none are
          dropped or merged (see §5.2: both Department Head AND HR Director).
        - Any clause that cannot be paraphrased without meaning loss is quoted
          verbatim, prefixed with [VERBATIM – paraphrase would alter meaning].
        - No phrase, fact, or obligation absent from the input sections appears
          in the output.
    error_handling: >
      If the input list is empty or any section has a missing/blank body,
      do not guess or fill in from external knowledge. Return:
        { "error": "INCOMPLETE_INPUT", "clause_id": "<affected id>",
          "message": "Clause body missing — cannot summarise safely." }
      If a clause body is ambiguous but present, apply the verbatim fallback
      rule rather than interpreting it.
