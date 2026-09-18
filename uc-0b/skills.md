skills:
  - name: retrieve_policy
    description: Load the HR leave policy document and return its content as structured numbered sections.
    input: Policy file path in text format, specifically ../data/policy-documents/policy_hr_leave.txt.
    output: Structured policy sections preserving every numbered clause, including clause references and complete conditions.
    error_handling: If the policy file is missing, unreadable, or ambiguous, do not guess; report the problem and stop.

  - name: summarize_policy
    description: Produce a concise policy summary that faithfully preserves every required clause, obligation, condition, threshold, and binding verb.
    input: Structured numbered sections retrieved from policy_hr_leave.txt.
    output: A clause-referenced summary saved as summary_hr_leave.txt with every numbered clause present and all multi-condition requirements preserved.
    error_handling: If a clause is ambiguous or cannot be summarized without meaning loss, quote it verbatim and flag it; never omit, weaken, or invent policy information.