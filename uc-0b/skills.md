skills:
  - name: retrieve_policy
    description: Loads the HR Leave Policy .txt file from the given path and returns its content as structured, numbered sections ready for clause-level processing.
    input: >
      A file path string pointing to the policy document
      (e.g. `../data/policy-documents/policy_hr_leave.txt`). Plain string, no
      additional formatting required.
    output: >
      Structured text: the full document content with each clause retained
      under its original numbering (e.g. 2.3, 5.2). Returned as a string of
      numbered sections; no clauses are merged, reordered, or omitted.
    error_handling: >
      If the file is missing, empty, or unreadable, do NOT attempt to generate
      or infer content. Return an explicit error signal so that the calling
      agent can respond with: "Source document could not be loaded.
      Summarisation aborted."

  - name: summarize_policy
    description: Takes the structured, numbered sections from `retrieve_policy` and produces a clause-faithful summary that preserves all binding verbs and multi-condition obligations.
    input: >
      The structured numbered-section string returned by `retrieve_policy`.
      Must include all 10 tracked clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2,
      3.4, 5.2, 5.3, 7.2). No external text or context should be passed in.
    output: >
      A written summary in which:
      - Every clause is referenced by its clause number.
      - Binding verbs (must, will, requires, not permitted) are preserved
        verbatim or with equivalently strong language — never softened.
      - All conditions in multi-condition obligations are retained
        (e.g. clause 5.2 must name BOTH Department Head AND HR Director).
      - No information absent from the source document is introduced.
      - Any clause that cannot be paraphrased without meaning loss is quoted
        verbatim and prefixed with [VERBATIM — meaning-loss risk].
    error_handling: >
      If the input is empty, malformed, or missing any of the 10 required
      clauses, refuse to produce a partial summary. Return an explicit error
      identifying which clauses are absent so the caller can re-invoke
      `retrieve_policy` or halt with an error message.
