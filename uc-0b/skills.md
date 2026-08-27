# skills.md

skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and converts it into a structured object indexed by section and clause numbers for easy auditing.
    input: file_path (string)
    output: A structured object mapping clause IDs (e.g., "2.3") to their full textual content.
    error_handling: Aborts with a clear error if the file is missing or lacks the expected numbered structure.

  - name: summarize_policy
    description: Produces a summary that preserves 100% of the obligations, dual-approver requirements, and time limits from the ground truth clauses.
    input: structured_clauses (object)
    output: A summary string where every listed clause title is followed by its summarized obligation or a verbatim quote.
    error_handling: If a clause like 5.2 (dual approval) is detected, the skill is restricted from using any phrasing that drops one of the approvers.
