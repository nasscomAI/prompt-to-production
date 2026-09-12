# skills.md

skills:
  - name: retrieve_policy
    description: Loads policy_hr_leave.txt and returns its content as structured numbered sections.
    input: Path to the policy .txt file.
    output: Structured numbered policy sections preserving clause numbers and source wording.
    error_handling: If the file is missing, unreadable, or malformed, do not invent content; report the problem and require review.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Structured numbered policy sections.
    output: A concise summary containing every numbered clause, with all conditions, binding obligations, exceptions, deadlines, thresholds, approvers, and prohibitions preserved.
    error_handling: If any clause cannot be summarized without meaning loss, quote it verbatim and mark it NEEDS_REVIEW. Never silently omit, weaken, or invent information.
