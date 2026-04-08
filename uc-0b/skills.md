# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: >
      input_path (str): path to the policy text file (e.g., policy_hr_leave.txt).
    output: >
      A list of structured sections, each containing the section number (e.g., 2.3),
      the section heading, and the full text of that clause. Preserves all numbered
      clauses exactly as they appear in the source.
    error_handling: >
      If the file is missing or unreadable, exit with a clear error message. If the
      file contains no recognizable numbered sections, warn and return the raw text
      as a single section for manual review.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all conditions and binding verbs.
    input: >
      sections (list): structured numbered sections from retrieve_policy.
    output: >
      A text summary (written to summary_hr_leave.txt) where every numbered clause
      is represented, each summary line references its source clause number, binding
      verbs are preserved at original strength, and multi-condition obligations
      retain all conditions.
    error_handling: >
      If a clause cannot be summarized without meaning loss, quote it verbatim and
      flag it with "[VERBATIM — meaning loss risk]". If a multi-condition clause
      is detected (e.g., clause 5.2 with two approvers), explicitly verify all
      conditions are present in the summary before finalizing.
