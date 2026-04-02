skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content parsed into structured numbered sections.
    input: >
      File path to a plain-text policy document (e.g. policy_hr_leave.txt).
      The file must be UTF-8 encoded and structured with numbered clause headings
      (e.g. 2.3, 3.4, 5.2).
    output: >
      A structured list of sections, each containing:
      clause_id (string, e.g. "2.3"), heading (string), and body (string — the
      full verbatim text of that clause as it appears in the source file).
    error_handling: >
      If the file is not found, raise a FileNotFoundError with the attempted path
      and halt — do not proceed to summarisation with an empty or partial input.
      If the file is found but contains no detectable numbered clause structure,
      return the entire document as a single unparsed block tagged clause_id: UNSTRUCTURED
      and flag it for manual review — do not silently discard content.
      If any clause cannot be fully parsed, include it as raw text with a PARSE_ERROR
      flag rather than omitting it — clause omission is a violation.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant clause-by-clause summary with clause references, preserving all obligations and conditions.
    input: >
      A structured list of sections as returned by retrieve_policy — each item
      contains clause_id, heading, and body (verbatim clause text from the source).
    output: >
      A plain-text summary file (summary_hr_leave.txt) with one entry per clause,
      each prefixed by its clause_id, preserving the binding verb (must, will,
      requires, not permitted, may, are forfeited), all named conditions, and all
      named parties. Clauses that cannot be summarised without meaning loss are
      output verbatim and tagged VERBATIM.
    error_handling: >
      If a clause contains multiple conditions (e.g. requires TWO named approvers),
      all conditions must be preserved in the output — if they cannot all be preserved
      in a paraphrase, quote the clause verbatim and tag it VERBATIM.
      If the input contains no sections, halt and return an error — do not produce
      an empty output file.
      If a clause body is empty or malformed, include the clause_id in the output
      with body: MISSING and flag: NEEDS_REVIEW — never silently skip a clause.
      Never add content not present in the input sections — any output text not
      traceable to a clause body is a scope-bleed violation and must be rejected.
