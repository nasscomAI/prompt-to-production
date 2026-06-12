skills:
  - name: retrieve_policy
    description: Loads policy_hr_leave.txt and returns the policy as structured numbered clauses for downstream summarization.
    input: A file path or raw text for ../data/policy-documents/policy_hr_leave.txt.
    output: Structured clause data keyed by clause number, preserving the original wording and section numbering.
    error_handling: If the file is missing, unreadable, or not the HR leave policy, fail explicitly and do not infer or substitute content.

  - name: summarize_policy
    description: Produces a clause-preserving summary of the HR leave policy with all required obligations, conditions, and prohibitions intact.
    input: Structured clause data from retrieve_policy.
    output: summary_hr_leave.txt content that includes every required numbered clause, keeps multi-condition obligations complete, and avoids unsupported additions.
    error_handling: If a clause cannot be summarized without meaning loss, emit the clause verbatim and mark it VERBATIM_REQUIRED; if input is incomplete, fail explicitly rather than guessing.
