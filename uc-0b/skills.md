# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Ingests the raw `.txt` policy file and structures the text logically into mapped, numbered sections to prevent clause omission during processing.
    input: File path to the raw `.txt` policy document (e.g., `policy_hr_leave.txt`).
    output: A structured JSON format or dictionary where keys are the specific clause identifiers (e.g. "2.3") mapping cleanly to the full string obligations.
    error_handling: Halts and raises an error if the document is unreadable or lacks clear numbered statutory structuring.

  - name: summarize_policy
    description: Iterates sequentially over the structured policy clauses to produce a strict, binding summary without softening active language or implicitly dropping compound conditions.
    input: Structured policy mapping outputted by the `retrieve_policy` skill.
    output: A formatted document output where every numbered target clause is cited, multi-conditions are kept intact, and exceedingly complex clauses are successfully quoted verbatim.
    error_handling: Strictly cross-verifies the final summary output against the input clauses. If an input clause is completely missing from the output text, it automatically triggers a retry or injects the raw clause directly into the final render padded with an [OMISSION_WARNING].
