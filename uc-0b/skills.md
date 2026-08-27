# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured, numbered sections for precise mapping.
    input: Absolute or relative path to a policy text file (e.g., policy_hr_leave.txt).
    output: A data structure (list or dictionary) containing all numbered clauses and their associated text.
    error_handling: Refuses to process if the file is missing, empty, or lacks distinct numbered sections (e.g., 2.3, 5.2).

  - name: summarize_policy
    description: Takes structured policy sections and produces a summary that adheres to all preservation rules and clause references.
    input: Structured policy data from retrieve_policy.
    output: A markdown or text summary where every clause is accounted for and conditions are preserved.
    error_handling: Explicitly flags and quotes verbatim any clause that cannot be accurately summarized without meaning loss.
