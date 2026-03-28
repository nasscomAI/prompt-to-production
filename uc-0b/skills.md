# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Ingests the policy text file and parses it into a machine-readable format to ensure no numbered clause is skipped during summarization.
    input: Absolute path to the .txt policy source file.
    output: A collection of structured sections indexed by clause number.
    error_handling: Identifying and flagging any section that lacks numbering or has ambiguous clause boundaries.

  - name: summarize_policy
    description: Transforms the structured sections into a condensed summary that strictly adheres to the enforcement rules in agents.md.
    input: Structured clause-content pairs provided by retrieve_policy.
    output: A final summary string that highlights every mandate and preserves every required approver and condition.
    error_handling: Explicitly quoting and flagging as '[FLAG: VERBATIM]' any clause that cannot be condensed without losing the core obligation.
