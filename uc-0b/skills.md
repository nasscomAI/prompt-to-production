

skills:
  - name: summarize_policy
    description: Produces a concise, meaning-preserving summary of the provided HR leave policy while retaining all material rules and constraints.
    input: A single HR leave policy document as plain text or structured text containing sections, clauses, and policy statements.
    output: A concise summary in plain text that preserves approvals, deadlines, thresholds, prohibitions, and consequences from the source document.
    error_handling: If the input is missing, incomplete, or contains clauses that cannot be safely compressed without losing meaning, preserve those clauses in near-original wording instead of over-summarizing or guessing.

  - name: validate_policy_summary
    description: Checks whether the generated summary faithfully preserves all critical policy conditions and compliance language from the source text.
    input: The original HR leave policy document and the generated summary as plain text.
    output: A validated summary result that confirms all material approvals, deadlines, thresholds, prohibitions, and consequences are retained.
    error_handling: If required conditions, approvers, deadlines, or prohibitive terms are missing, softened, or ambiguous, reject the summary and restore the affected clause in clearer or near-original wording.
