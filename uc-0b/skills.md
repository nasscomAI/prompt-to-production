skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: input_path (path to a policy .txt file such as ../data/policy-documents/policy_hr_leave.txt).
    output: An ordered list of (clause_id, body_text) tuples parsed from the numbered X.Y clauses, with continuation lines joined and whitespace normalised.
    error_handling: Missing or unreadable file prints an error to stderr and exits with status 1. Lines that are section dividers or unnumbered headings are skipped.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references.
    input: A list of (clause_id, body_text) tuples as returned by retrieve_policy.
    output: An ordered list of (clause_id, summary_text, flagged) where every clause is covered, multi-condition obligations keep all conditions, and clauses without a safe summary are quoted verbatim with flagged=True.
    error_handling: Clause ids in the summary table that do not exist in the source are reported as a warning to stderr; the output is still written with every parsed clause covered.