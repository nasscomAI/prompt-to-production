skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content as a structured list of numbered sections, preserving all clause numbers and original wording.
    input: >
      File path (string) pointing to a .txt policy document, e.g.
      ../data/policy-documents/policy_hr_leave.txt.
    output: >
      A structured representation of the document as an ordered list of
      sections, each containing: section_number (string, e.g. "2.3"),
      heading (string or blank), and body (string — the full original text
      of that clause, unmodified).
    error_handling: >
      If the file does not exist or cannot be read, raise a descriptive error
      and halt — do not return partial content.
      If the file is empty, raise an error stating the document contains no
      content to process.
      If a section cannot be assigned a clause number (e.g. unnumbered
      introductory text), include it as a section with section_number set to
      "preamble" so no content is silently dropped.
      Never attempt to infer missing clause numbers from context or external
      knowledge.

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and generates a clause-faithful summary that preserves every obligation, condition, and binding verb exactly as stated in the source.
    input: >
      An ordered list of structured sections as returned by retrieve_policy,
      each with fields: section_number, heading, body.
      Also accepts the ground-truth clause checklist: [2.3, 2.4, 2.5, 2.6,
      2.7, 3.2, 3.4, 5.2, 5.3, 7.2].
    output: >
      A plain-text summary written to uc-0b/summary_hr_leave.txt. Each entry
      in the summary must: (1) open with the original clause number, (2) state
      the obligation using the source binding verb (must / will / requires /
      not permitted), and (3) preserve all named conditions and parties.
      Any clause that cannot be summarised without meaning loss must be quoted
      verbatim and appended with the flag:
      [VERBATIM — summarisation would cause meaning loss].
    error_handling: >
      Clause omission: before writing output, verify all 10 ground-truth
      clauses are present. If any clause is missing from the structured input,
      raise a warning naming the missing clause number and halt — do not
      produce a summary with silent omissions.
      Obligation softening: if the summarisation step would replace a binding
      verb (must, will, requires, not permitted) with a weaker form (should,
      may, is expected to), quote the clause verbatim instead and append the
      VERBATIM flag.
      Condition drop: if a multi-condition obligation (e.g. clause 5.2
      requiring BOTH Department Head AND HR Director) cannot be preserved in
      full, quote the clause verbatim and append the VERBATIM flag — never
      silently drop a condition.
      Scope bleed: if any generated sentence contains information not traceable
      to the source document — including phrases like "as is standard practice",
      "typically in government organisations", or "employees are generally
      expected to" — remove that sentence entirely and do not include it in
      the output.
